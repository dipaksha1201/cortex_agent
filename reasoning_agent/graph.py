from langgraph.graph import END, StateGraph, START
from reasoning_agent.prompt import PROMPTS
from reasoning_agent.services import create_reasoning_text, format_relationships, retrieve_subqueries
from utils import gemini_flash
from reasoning_agent.models import FinalAnswer, OverallState, Subqueries
from langgraph.config import get_stream_writer

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

def aggregate_subquery_results(state: OverallState):
    subquery_results = state.get("subquery_results", [])
    relationships = [format_relationships(response["data"]["relationships"], response["query"]) for response in subquery_results if response["type"] == "response"]
    formatted_relationships = "\n".join(relationships)
    prompt = PROMPTS["aggregate_subquery_results"].format(original_query=state["query"], formatted_reasoning_steps=formatted_relationships)
    final_response = gemini_flash.with_structured_output(FinalAnswer).invoke(prompt)
    result = create_reasoning_text(subquery_results, final_response)
    print("printing result")
    print(result)
    return {"final_answer": result}

# Construct the graph: here we put everything together to construct our graph
graph = StateGraph(OverallState)
graph.add_node("generate_subqueries", generate_subqueries)
graph.add_node("aggregate_subquery_results", aggregate_subquery_results)
graph.add_node("retrieve_subqueries", node_retrieve_subqueries)
graph.add_edge(START, "generate_subqueries")
graph.add_edge("generate_subqueries", "retrieve_subqueries")
graph.add_edge("retrieve_subqueries", "aggregate_subquery_results")
graph.add_edge("aggregate_subquery_results", END)

# Compile the graph
knowledge_engine = graph.compile()