from langchain_google_genai import ChatGoogleGenerativeAI
import os

def getLLM(model):
    if model == 'gemini':
        api_key=os.getenv("GOOGLE_API_KEY")
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key)
        return llm

