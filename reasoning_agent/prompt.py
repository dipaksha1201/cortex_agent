"""Prompts."""

from typing import Any, Dict

PROMPTS: Dict[str, Any] = {}

# Prompts we will use
PROMPTS["generate_subqueries"] = """You are an expert at converting user questions into database queries and queries for a vectorstore.
    You have access to a database of information about LLMs. 

    Your task involves two responsibilities:
    1. Perform query decomposition: Given a user question, break it down into distinct sub-questions that you need to 
    answer in order to address the original question. Ensure the sub-questions are clear and distinct.
    2. Convert queries for a vectorstore: For each sub-question, strip out information that is not relevant to the retrieval task and convert it into a query suitable for a vectorstore.

    Additional Instructions:
    - If there are acronyms or words you are not familiar with, do not try to rephrase them.
    - Ensure that each query or sub-question is actionable and specific for efficient retrieval.

    Here is the user query: {query}
"""
    
PROMPTS["aggregate_subquery_results"] = """
        You have been provided with an original query and a series of subquery contexts.
        Each subquery includes a smaller query, some properties, and contextual information.

        Original Query:
        {original_query}

        Subquery Contexts:
        {formatted_reasoning_steps}

        Instructions:
        1. Think and plan about the original query and the subqueries.
        2. Combine and synthesize the insights from each subquery.
        3. Draft a conclusive answer that addresses the "Original Query" thoroughly.
        4. Be detailed, accurate, and informative in your response.
        5. Return a properly formatted text string as your final answer.
        6. Dont create synthetic data or make up any information. Strictly follow the context provided.
        7. If you are not sure about the answer, just say "I don't know" or "I don't have information about that".
        8. You dont have to give the sources.
        9. Be as detailed, explanatory and insightful as possible.

        Do not include any extra text or markdown;
        Final Answer:
        
        """

