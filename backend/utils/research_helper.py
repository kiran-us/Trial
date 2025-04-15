from backend.tools.tavily import tavily_tool
#from backend.tools.vector_store import retriever_tool
from backend.tools.web_scraper import bs4_scraper
from backend.tools.playwright import playwright_web_tool
from langchain.agents import AgentExecutor, create_react_agent
import re
import json



tools=[playwright_web_tool]





def format_filters(filters_str):
    """Formats a string of filters into a list of formatted lines."""
    if not filters_str:
        return "No filters provided."
    filter_lines = [f" - {filter_item.strip()}" for filter_item in filters_str.split(",")] #split the string into a list.
    return "\n".join(filter_lines)

def format_notes(notes_list):
    """Formats a list of notes into a string of formatted lines."""
    if not notes_list:
        return "No notes provided."
    note_lines = [f" - {note.strip()}" for note in notes_list]
    return "\n".join(note_lines)

def run_research_task(title,primary_search_terms,search_strategy,target_locations,data_extraction_format,verification_process,metadata_requirements, llm, prompt, vector_store):
    response=""
    
   
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,
                                   handle_parsing_errors=True,
                                  max_iterations=30,max_execution_time=600)

    # Run the agent
    response = agent_executor.invoke({
        "input": title,
        "primary_search_terms": primary_search_terms,
        "search_strategy": search_strategy,
        "target_locations": target_locations,
        "data_extraction_format": data_extraction_format,
        "verification_process": verification_process,
        "metadata_requirements": metadata_requirements,
        "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in tools]),
        "tool_names": ", ".join([tool.name for tool in tools])
    })

    # Extract and clean the output (assuming the agent outputs JSON within its final response)
    response_content = response["output"]

    cleaned_json = re.sub(r"```json\n|```", "", response_content).strip()

    data = json.loads(cleaned_json)
    print("response", response_content)
    return data



def run_reviewer_task(jobs, llm, prompt):
    response=""

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,
                                   handle_parsing_errors=True,
                                   max_iterations=len(jobs) * 3)
    # Run the agent
    response = agent_executor.invoke({
       "input": f"Find details of each listings using jobs list",
        "jobs": jobs,
        "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in tools]),
        "tool_names": ", ".join([tool.name for tool in tools])
    })


    print("reviewer task",response["output"])
        
    # Extract and clean the output (assuming the agent outputs JSON within its final response)
    response_content = response["output"]

    cleaned_json = re.sub(r"```json\n|```", "", response_content).strip()

    data = json.loads(cleaned_json)

    return data
