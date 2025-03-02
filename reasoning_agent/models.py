from typing import TypedDict
from pydantic import BaseModel, Field
from typing_extensions import Annotated
import operator
    
class Subqueries(BaseModel):
    subqueries: list[str] = Field(description="a list of strings, each string is a subquery generated from the user query")

class FinalAnswer(BaseModel):
    final_answer: str = Field(description="a string, a detailed answer to the user query")
    
class OverallState(TypedDict):
    query: str
    subqueries: list[str]
    subquery_results: list[dict]
    final_answer: str