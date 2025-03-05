from langgraph.graph import END, StateGraph, START
from tools.google_search import google_search
from reasoning_agent.prompt import PROMPTS
from reasoning_agent.services import create_reasoning_text, format_relationships, retrieve_subqueries
from tools.table_operator import table_operator
from utils import gemini_flash, gemini_flash_thinking
from reasoning_agent.models import CheckTable, OverallState, Subqueries
from langgraph.config import get_stream_writer
from utils.logger_config import cortex_logger

def generate_subqueries(state: OverallState):
    prompt = PROMPTS["generate_subqueries"].format(query=state["query"])
    response = gemini_flash.with_structured_output(Subqueries).invoke(prompt)
    return {"subqueries": response.subqueries}

# Your LangGraph node that calls retrieve_subqueries and streams its output
async def node_retrieve_subqueries(state: OverallState):
    # Assume the list of subqueries is in state["queries"]
    queries = state.get("subqueries", [])
    subquery_results = []
    writer = get_stream_writer()
    async for output in retrieve_subqueries(queries):
        # Yield each piece of the response to stream downstream
        subquery_results.append(output)
        writer({"retriever_updates": output})
    
    return {"subquery_results": subquery_results}

def internet_search(state: OverallState):
    subquery_results = state.get("subquery_results", [])
    reasoning_text = create_reasoning_text(subquery_results)
    prompt = PROMPTS["internet_search"].format(query=state["query"], subqueries=reasoning_text)
    response = gemini_flash.with_structured_output(Subqueries).invoke(prompt)
    writer = get_stream_writer()
    for subquery in response.subqueries:
        writer({"retriever_updates": {"query": subquery + " (online search)"}})
        search_response = google_search(subquery)
        writer({"retriever_updates": {"response": search_response}})
        subquery_results.append({"type": "response", "query": subquery + " (online search)", "response": search_response})
        
    return {"subquery_results": subquery_results}

def aggregate_subquery_results(state: OverallState):
    subquery_results = state.get("subquery_results", [])
    reasoning_text = create_reasoning_text(subquery_results)
    if state.get("enable_search", False):
        prompt = PROMPTS["aggregate_subquery_results"].format(original_query=state["query"], formatted_reasoning_steps=reasoning_text)
    else:
        prompt = PROMPTS["aggregate_subquery_results_with_search"].format(original_query=state["query"], formatted_reasoning_steps=reasoning_text)

    table = "empty"
    if state.get("show_table", False):
        table = table_operator(reasoning_text)
    else:
        check_table = gemini_flash.with_structured_output(CheckTable).invoke(PROMPTS["aggregate_subquery_results_with_table"].format(original_query=state["query"], formatted_reasoning_steps=reasoning_text))
        if check_table.check_table:
            table = table_operator(reasoning_text)

    final_response = gemini_flash_thinking.invoke(prompt)
    cortex_logger.info(f"Final response from reasoning agent: {final_response}")
    cortex_logger.info(f"Table from reasoning agent: {table}")
    return {"final_answer": final_response.content, "table": table}

def is_internet_search_required(state: OverallState):
    enable_search = state.get("enable_search", False)
    if enable_search:
        return "internet_search"
    else:
        return "aggregate_subquery_results"

# Construct the graph: here we put everything together to construct our graph
graph = StateGraph(OverallState)
graph.add_node("internet_search", internet_search)
graph.add_node("generate_subqueries", generate_subqueries)
graph.add_node("aggregate_subquery_results", aggregate_subquery_results)
graph.add_node("retrieve_subqueries", node_retrieve_subqueries)
graph.add_node("is_internet_search_required", is_internet_search_required)
graph.add_edge(START, "generate_subqueries")
graph.add_edge("generate_subqueries", "retrieve_subqueries")
graph.add_conditional_edges("retrieve_subqueries", is_internet_search_required)
graph.add_edge("internet_search", "aggregate_subquery_results")
graph.add_edge("aggregate_subquery_results", END)

# Compile the graph
knowledge_engine = graph.compile()