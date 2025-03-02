import os
from pydantic import Field
import logging
from reasoning_agent import knowledge_engine
from cortex_agent.prompts import PROMPTS
from utils import gemini_flash
from langchain_core.tools import tool
from typing_extensions import Annotated
from langgraph.prebuilt import create_react_agent
from utils.pinecone import PineconeStore
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.mongodb import AsyncMongoDBSaver      

# Get the logger but only configure it if it doesn't already have handlers
app_logger = logging.getLogger("app_logger")
if not app_logger.handlers:
    app_logger_file_path = os.path.join("./logs", "app_dev.log")
    app_logger.setLevel(logging.INFO)
    # app_logger.format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    app_logger.addHandler(logging.FileHandler(app_logger_file_path, mode='a'))
    app_logger.addHandler(logging.StreamHandler())

InternalKnowledgeSearch = Annotated[str, Field(description="Search the internal knowledge base for the given query.")]

store = PineconeStore().get_vector_store("cortex-memory")

@tool
async def internal_knowledge_search(query: InternalKnowledgeSearch):
    """Search the internal knowledge base for the query."""
    
    result = ""
    async for s in knowledge_engine.astream({"query": query} , stream_mode="updates"):
        if "final_answer" in s:
            result = s["final_answer"]
            
    return result

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

async def run_cortex(inputs, config):
    async with AsyncMongoDBSaver.from_conn_string(os.getenv("MONGODB_URI")) as checkpointer:
        cortex = create_react_agent(
                    model=gemini_flash,
                    tools=[internal_knowledge_search],
                    prompt=SystemMessage(PROMPTS["cortex"]),
                    checkpointer=checkpointer,
                    store=store,
                    )

        async for s in cortex.astream(inputs, config, stream_mode="custom"):
            if "retriever_updates" in s:
                if "response" in s["retriever_updates"]:
                    app_logger.info("\n---------------INTERNAL SEARCH UPDATES RESPONSE-----------------\n")
                    app_logger.info(s["retriever_updates"]["response"])
                    app_logger.info("--------------------------------")
                elif "query" in s["retriever_updates"]:
                    app_logger.info("\n---------------QUERY-----------------\n")
                    app_logger.info(s["retriever_updates"]["query"])
                    app_logger.info("--------------------------------")
            elif "final_answer" in s:
                app_logger.info("\n---------------FINAL ANSWER-----------------\n")
                app_logger.info(s["final_answer"])
                app_logger.info("--------------------------------")

                
        state = await cortex.aget_state(config=config)
        
        app_logger.info("---------------Cortex State--------------")
        app_logger.info(state)
        app_logger.info("--------------------------------")
        
        return state.values["messages"][-1].content

