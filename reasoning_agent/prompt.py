"""Prompts."""

from typing import Any, Dict

PROMPTS: Dict[str, Any] = {}

# Prompts we will use
PROMPTS["generate_subqueries"] = """You are an expert at generating precise, relevant, and efficient queries for vector databases based on user questions and the context of multiple uploaded documents. Your goal is to ensure comprehensive coverage and specificity in retrieving the most relevant data possible, even when the initial user query appears ambiguous.

Your Responsibilities:

1. Query Decomposition:
Break down the provided user query into clear, distinct, and actionable sub-questions.
Ensure each sub-question is necessary and directly contributes to answering the original query comprehensively.
Avoid redundancy: Sub-questions must not be duplicates or overly similar.
Always use multi-hop query decomposition where necessary, clearly outlining logical steps or dependencies between queries.
2. Conversion to Vectorstore Queries:
Convert each sub-question into an optimized, concise query suitable for vectorstore retrieval.
Eliminate unnecessary or irrelevant details that do not aid the retrieval process.
Keep queries focused, specific, and actionable.

Important Guidelines:
Leverage the complete context and knowledge from all previously uploaded documents to inform query generation.
If the user's original query seems ambiguous, utilize your contextual knowledge to clarify and formulate explicit vectorstore queries that accurately reflect possible intents.
Queries must be distinct and non-overlapping to maximize the efficiency of data retrieval.
Generate as few queries as needed, but ensure completeness of coverage.

**Ingested Documents Information:**
{database_info}

**User Query:**
{user_query}
"""
    
PROMPTS["aggregate_subquery_results"] = """
            You have been provided with an **Original Query** along with a series of **Subquery Contexts**.  
            Each subquery includes a **smaller query**, some **properties**, and **contextual information**.  

            ---

            ### **Input Data:**  

            🔹 **Original Query:**  
            {original_query}  

            🔹 **Subquery Contexts:**  
            {formatted_reasoning_steps}  

            ---

            ### **Instructions:**  

            1 **Understand the Context**  
            - Analyze the **Original Query** to determine the overall intent.  
            - Examine all **subqueries** and their **context** carefully.  

            2 **Synthesize Insights**  
            - Combine and **synthesize** information from all subqueries.  
            - Ensure a **cohesive, structured, and insightful** response.  
            - Identify **patterns, correlations, or contradictions** if any.  

            3 **Generate a Conclusive Answer**  
            - Draft a **detailed, accurate, and well-structured** response.  
            - Ensure the answer **directly addresses the Original Query**.  
            - Avoid unnecessary repetition—**focus on clarity and depth**.  

            4 **Strict Adherence to Context**  
            - **Do NOT generate synthetic data** or make up information.  
            - **Only rely on the provided subquery contexts**—no external assumptions.  
            - If the information is **insufficient**, respond with:  
                - *"I don't know"* or *"I don’t have information about that."* and prompt the user to proceed with an online search.  

            5 **Formatting & Output**  
            - Return a **well-written, professional, and explanatory** answer.  
            - Avoid mentioning sources or subqueries explicitly.  
            - **DO NOT** include extra text, markdown, or unnecessary disclaimers.  

            ---

            ### **Final Answer:**  
                    
        """

PROMPTS["aggregate_subquery_results_with_search"] = """You have been provided with an **Original Query** and a set of **Subquery Contexts**, which include:  
- **RAG-Based Subqueries** → Information retrieved from internal documents.  
- **Online Search Subqueries (tagged as "(online search)")** → Information sourced from the internet.  

---

### **Input Data:**  

🔹 **Original Query:**  
{original_query}  

🔹 **Subquery Contexts:**  
{formatted_reasoning_steps}  

---

### **Instructions:**  

1 **Analyze & Plan**  
   - Understand the **intent** of the **Original Query**.  
   - Examine all **subqueries**, giving **special attention** to RAG-based subqueries.  
   - Identify **how RAG-based insights and online search results connect** to provide a **cohesive, factually supported answer**.  

2 **Synthesize Insights from Different Sources**  
   - **RAG-Based Insights** → Extract validated information from retrieved documents.  
   - **Online Search Results** → Verify, update, and complement RAG data with the latest external findings.  
   - **Cross-Reference Data** →  
     - If RAG and online search results align, **reinforce the insight with external validation**.  
     - If there are discrepancies, **highlight them and provide a reasoned perspective**.  

3 **Construct a Clear, Informative Answer**  
   - Integrate **both RAG-based and online search insights** in a **structured, logical flow**.  
   - Ensure the response is:  
     ✅ **Comprehensive** – Covers all key aspects of the original query.  
     ✅ **Well-Connected** – Shows how retrieved document data (RAG) aligns or differs from external sources.  
     ✅ **Contextually Clear** – Explicitly **differentiate RAG-based information from online search insights**.  
     ✅ **Insightful & Actionable** – Ensure the final response **makes sense and provides direct value to the user**.  

4 **Strict Context Adherence**  
   - **DO NOT** generate synthetic data or speculate.  
   - **DO NOT** ignore inconsistencies—highlight and explain them.  
   - If available information is **insufficient**, respond with:  
     - *"I don't know"* or *"I don’t have information about that."*  

5 **Formatting & Output**  
   - **Clearly distinguish RAG-based insights as Internal Knowledge from online search results** in the response.  
   - Maintain a **coherent, easy-to-understand flow**.  
   - **DO NOT** include extra text, markdown, or unnecessary disclaimers.  

---

### **Final Answer:**  """

PROMPTS["aggregate_subquery_results_with_table"] = """You have been provided with an **Original Query** and a set of **Subquery Contexts**, which include:  
- **RAG-Based Subqueries** → Information retrieved from internal documents.  
- **Online Search Subqueries (tagged as "(online search)")** → Information sourced from the internet.  

---

### **Input Data:**  

🔹 **Original Query:**  
{original_query}  

🔹 **Subquery Contexts:**  
{formatted_reasoning_steps}  

---

### **Instructions:**  
Based on the provided information decide if a table is required or not.
"""

PROMPTS["internet_search"] = """
    You have been provided with a **main query** along with a list of **subqueries** and their respective responses. Your task is to generate **insight-driven, highly creative, and context-aware search queries** that:  

    ### **Key Objectives:**  
    1. **Follow Explicit Search Instructions** – If the main query includes specific requirements for search, ensure that all queries align with those instructions.  
    2. **Validate & Cross-Check** – Verify the accuracy, credibility, and relevance of retrieved responses from subqueries.  
    3. **Discover Hidden Insights & Gaps** – Formulate queries that uncover overlooked details, rare perspectives, or niche findings.  
    4. **Challenge Assumptions & Biases** – Search for contradictory viewpoints, limitations, ethical concerns, or industry debates.  
    5. **Explore Emerging Trends & Future Implications** – Investigate innovations, expert analyses, and market shifts related to the topic.  

    ### **Instructions:**  
    - **If the main query provides specific guidelines on how to search, prioritize those while still maintaining depth and creativity.**  
    - If no clear intent is stated, infer **the underlying goal** based on subqueries and retrieved responses.  
    - Generate queries that encourage **multi-dimensional exploration**, such as:  
    - Opposing viewpoints  
    - Alternative explanations  
    - Advanced technical insights  
    - Ethical & legal implications  
    - Historical comparisons & future projections  
    - Avoid duplicate queries 
    - Generate at least 2 queries that are not similar to the main query but are related to the main query
    - Generate upto 5 queries at max and try to generate queries that are not similar to each other
    - **Think beyond verification—aim to extract valuable insights, validations, and strategic intelligence.**  

    ---

    ### **Input Data:**  

    🔹 **Main Query (with possible search instructions):**  
    {query}  

    🔹 **Subqueries & Retrieved Responses:**  
    {subqueries}  

    ---

    ### **Your Task:**  
    Based on the provided information, generate **high-impact, well-structured, and deeply insightful search queries** that:  
    ✅ Align with explicit instructions (if any)  
    ✅ Verify retrieved responses  
    ✅ Expand perspectives & challenge biases  
    ✅ Surface expert-backed insights, trends, and strategic takeaways  
"""