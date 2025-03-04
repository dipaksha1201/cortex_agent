import os
from pydantic import Field
import logging
from reasoning_agent import knowledge_engine
from cortex_agent.prompts import PROMPTS
from utils import gemini_flash, gemini_embeddings
from langchain_core.tools import tool
from typing_extensions import Annotated
from langgraph.prebuilt import create_react_agent
from utils.pinecone import PineconeStore
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.mongodb import AsyncMongoDBSaver      
from langmem import create_manage_memory_tool, create_search_memory_tool
from langgraph.store.postgres import AsyncPostgresStore
from utils.logger_config import cortex_logger

InternalKnowledgeSearch = Annotated[str, Field(description="Search the internal knowledge base for the given query.")]

@tool(return_direct=True)
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
    # manage_memory_tool = create_manage_memory_tool(namespace=("memories",f"{config['configurable']['user_id']}"))
    # search_memory_tool = create_search_memory_tool(namespace=("memories",f"{config['configurable']['user_id']}")) 
    async with AsyncMongoDBSaver.from_conn_string(os.getenv("MONGODB_URI")) as checkpointer:
        # async with AsyncPostgresStore.from_conn_string(
        # os.getenv("DB_URI"),
        # index={
        #     "dims": 768,
        #     "embed": gemini_embeddings,
        #     }
        # ) as store:
            cortex = create_react_agent(
                        model=gemini_flash,
                        tools=[internal_knowledge_search],
                        prompt=SystemMessage(PROMPTS["cortex"]),
                        checkpointer=checkpointer,
                        # store=store,
                    )

            async for s in cortex.astream(inputs, config, stream_mode="custom"):
                if "retriever_updates" in s:
                    if "response" in s["retriever_updates"]:
                        yield {"type": "response", "content": s["retriever_updates"]["response"]}
                    elif "query" in s["retriever_updates"]:
                        yield {"type": "query", "content": s["retriever_updates"]["query"]}
            
            state = await cortex.aget_state(config=config)
            cortex_logger.info(state.values)
            
            yield {"type": "complete", "content": state.values["messages"][-1].content}

