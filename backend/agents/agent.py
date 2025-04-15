from backend.states.state import SharedState
from backend.models.models import getLLM
from backend.prompts.prompts import planner_agent_prompt, research_agent_prompt, reviewer_agent_prompt
import re
from backend.utils.research_helper import run_research_task
#from backend.utils.db import load_existing_chroma_store
import json
from backend.utils.files import download_and_list_files


def planner_agent(state: SharedState):
    print("=========entering planner agent=========")

    title = state.get("title")
    llm = getLLM("gemini")

    rag_chain = planner_agent_prompt | llm

    response = rag_chain.invoke({"input":title })
    response_content = response.content
    print("response", response_content)
    # Step 1: Remove code block markers
    cleaned_json = re.sub(r"```json\n|```", "", response_content).strip()

    # Step 2: Safely fix newline issues
    # If the issue is caused by raw newlines inside strings, you can escape them:
    safe_json_string = re.sub(r'(?<!\\)"(?=[^:,}\]\n]*?\n)', r'\"', cleaned_json)
    safe_json_string = safe_json_string.replace("\n", "\\n")
    planner_data = json.loads(cleaned_json)
    state["planner_response"] = planner_data

    print("=========exiting planner agent=========")
    return state

def researcher_agent(state: SharedState):
    print("=========entering research agent=========")    
    data = state["planner_response"]


    # Extract search term
    primary_search_terms = data["primary_search_terms"]
    search_strategy= data["search_strategy"]
    target_locations = data["target_locations"]
    data_extraction_format = data["data_extraction_format"]
    verification_process = data["verification_process"]
    metadata_requirements = data["metadata_requirements"]


    input= state["title"]


    llm = getLLM("gemini")  # Initialize LLM
#    vector_store = load_existing_chroma_store(persist_directory)
    vector_store = None
    responses = run_research_task(input,primary_search_terms,search_strategy,target_locations,data_extraction_format,verification_process,metadata_requirements, llm, research_agent_prompt, vector_store)



    state["publisher_response"] = responses # Correctly store the responses dictionary
    print("=========exiting research agent=========")    
    return state


def executor_agent(state:  SharedState):
    print("=========starting executor agent=========")    
  #  report = generate_report(state["publisher_response"])
    response=state["publisher_response"]
    # print("=========executor jobs=========")
    # print(jobs)
    downloaded_file_paths = download_and_list_files(response)
    state["downloaded_files"] = downloaded_file_paths
    print("=========downloaded files=========")
    print(downloaded_file_paths)

    
    llm = getLLM("gemini")  # Initialize LLM

    rag_chain = reviewer_agent_prompt | llm

    response = rag_chain.invoke({"list": response})
    response_content = response.content

    state["executor_response"]= response_content
    print("=========exiting executor agent=========")    
    return state
