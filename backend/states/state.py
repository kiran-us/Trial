from typing import TypedDict, Annotated, List, Dict, Union
from langgraph.graph.message import add_messages

    
    
class SharedState(TypedDict, total=False):  # total=False makes all fields optional
    question: str
    title: str
    location: int
    conversation_message: Annotated[List, add_messages]
    planner_response: Dict
    research_input: str
    research_response: str
    publisher_input: str
    publisher_response: str
    executor_response:str
    jobs_length:str
#    persist_directory: list
    primary_search_terms: list
    search_strategy: str
    target_locations: list
    data_extraction_format: str
    verification_process:str
    metadata_requirements: list
    