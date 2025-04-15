#Create a workflow

from langgraph.graph import StateGraph, START, END
from backend.utils.generate_diagram import generate_diagram
from backend.agents.agent import planner_agent,researcher_agent, executor_agent
from backend.states.state import SharedState
#from backend.utils.db import create_local_chroma_from_file
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()


def should_continue(state: SharedState):
    """ Return the next node to execute """

    # Check if human feedback
    human_analyst_feedback=state.get('human_analyst_feedback', None)
    if human_analyst_feedback:
        return "researcher_agent"
    
    # Otherwise end
    return END

def init_func():
    print("starting server")
    global graph
    builder = StateGraph(SharedState)
    builder.add_node("planner_agent", planner_agent)
    builder.add_node("researcher_agent", researcher_agent)
    builder.add_node("executor_agent",executor_agent)    
    builder.add_edge(START, "planner_agent")
    builder.add_edge("planner_agent", "researcher_agent")
    builder.add_edge("researcher_agent", "executor_agent")
    builder.add_conditional_edges("executor_agent", should_continue, ["researcher_agent", END])
    graph = builder.compile(checkpointer=checkpointer)
   # generate_diagram(graph)


def handle_user_request(title: str):
    global graph
    print("=========entering handle_user_request=========")
    #persist_directory = create_local_chroma_from_file("./data_files/" + uploaded_filename)
    input_data = {
        "title": title,
        # "persist_directory": "./chroma_db"
    }

 
    result = graph.invoke(input=input_data,config={"configurable": {"thread_id": 1}})
    print("result",result)
    return result.get("executor_response")
    return "done"


