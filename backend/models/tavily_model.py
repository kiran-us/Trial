from tavily import TavilyClient
import os

def search_web(query):
    api_key=os.getenv("TAVILY_API_KEY")
    tavily_client = TavilyClient(api_key=api_key)
    response = tavily_client.search(query)
    print(response)
    return response