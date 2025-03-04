import httpx
from dotenv import load_dotenv
import os
import json

load_dotenv()

def format_relationships(relationships: list[dict], query: str) -> str:
    """
    Utility to convert a list of relationship objects into a formatted string.
    """
    # Sort relationships by score in descending order
    sorted_relationships = sorted(relationships, key=lambda x: x['score'], reverse=True)
    
    relationships_str = []
    query_str = f"----------------QUERY------------------\n{query}\n"
    relationships_str.append(query_str)
    
    for relationship in sorted_relationships:
        relationship_info = (
            f"----------------RELATIONSHIP------------------\n"
            f"{relationship['source']} -> {relationship['target']} (Score: {relationship['score']})\n"
            f"----------------DESCRIPTION------------------\n"
            f"{relationship['description']}\n"
            f"----------------EVIDENCE------------------\n"
            f"{''.join(relationship['chunks'])}\n"
        )
        relationships_str.append(relationship_info)
        
    return "\n".join(relationships_str)

def create_reasoning_text(subquery_results, final_response) -> str:
    reasoning_steps = []
    for response in subquery_results:
        if response["type"] == "response":
            reasoning_steps.append("---------------SUB-QUERY---------------")
            reasoning_steps.append(response["query"])
            reasoning_steps.append("---------------SUB-QUERY RESPONSE---------------")
            reasoning_steps.append(response["response"])
    reasoning_steps.append("---------------FINAL ANSWER---------------")
    reasoning_steps.append(final_response.content)
    return "\n".join(reasoning_steps)


async def retrieve_subqueries(queries: list[str]):
    url = f"{os.getenv('DOCSERVICE_BASE_URL')}/query"
    data = {
        "user_name": "dipak",
        "queries": queries
    }
    headers = {
        "Content-Type": "application/json",
        "Connection": "keep-alive"
    }

    # Disable default timeouts
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, json=data, headers=headers) as response:
            if response.status_code == 200:
                async for line in response.aiter_lines():
                    try:
                        parsed_line = json.loads(line)
                        yield parsed_line
                    except json.JSONDecodeError:
                        print("Failed to parse line:", line)
            else:
                print("Failed:", response.status_code, response.text)
