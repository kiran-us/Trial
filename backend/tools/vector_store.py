
from langchain.tools import Tool
from backend.utils.db import load_existing_chroma_store

vector_store = load_existing_chroma_store("../chroma_db")

def create_retriever_tool(vector_store, name="knowledge_base", description="Useful for answering questions about the content in the vector store. Input should be a fully formed question."):
    """Creates a retriever tool from a Chroma vector store."""
    retriever = vector_store.as_retriever()
    tool = Tool(
        name=name,
        func=retriever.get_relevant_documents,
        description=description,
    )
    return tool


retriever_tool = create_retriever_tool(
    vector_store,
    name="fda_labeler_code_knowledge",
    description="Search for FDA labeler codes, their metadata, and associated information from the FDA database."
)