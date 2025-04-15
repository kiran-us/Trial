import streamlit as st
import os

from langchain_community.document_loaders import CSVLoader, PyPDFLoader, UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
persist_directory="./chroma_db"

def create_local_chroma_from_file(filename):
    """
    Creates a Chroma vector store from a file already present in the local filesystem.
    `filename` should be a relative or absolute path (e.g., '../data_files/data.csv')
    """
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return None

    # Choose loader based on file extension
    if filename.endswith(".csv"):
        loader = CSVLoader(file_path=filename)
    elif filename.endswith(".pdf"):
        loader = PyPDFLoader(file_path=filename)
    elif filename.endswith((".xlsx", ".xls")):
        loader = UnstructuredExcelLoader(file_path=filename)
    else:
        print(f"Unsupported file type: {filename}")
        return None

    try:
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)

        if not chunks:
            print("No chunks created from file.")
            return None

        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        vector_store.persist()
        print(f"Vector store created at {persist_directory}")
        return persist_directory

    except Exception as e:
        print(f"Error processing file {filename}: {e}")
        return None



def load_existing_chroma_store(persist_directory="./chroma_db"):
    """Loads an existing Chroma vector store with Gemini embeddings."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return vector_store