from fastapi import FastAPI
from pydantic import BaseModel
from backend.app import init_func , handle_user_request
app = FastAPI()

# Define request structure
class ChatRequest(BaseModel):
    title: str = None
    file: str = None

@app.on_event("startup")
def startup_event():
    init_func()
    
# Dummy chatbot response
@app.post("/chat")
def chat_response(request: ChatRequest):

     # Replace with AI logic
    print("Connect to the backend")
    response = handle_user_request(
            request.title
    )
   
    return {"response": response}

# Run with: uvicorn api:app --reload
