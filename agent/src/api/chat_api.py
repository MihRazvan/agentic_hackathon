# agent/src/api/chat_api.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from ..ai.chatbot_agent import DAOAgent, AgentResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
agent = DAOAgent()

class ChatRequest(BaseModel):
    message: str
    address: str  # User's wallet address

@app.post("/api/chat", response_model=AgentResponse)
async def chat(request: ChatRequest):
    """Process chat messages and generate actions."""
    try:
        logger.info(f"Processing chat request from {request.address}")
        response = await agent.chat(request.message)
        
        # If there's an action, add the user's address to the context
        if response.action:
            # Add any additional context needed for the frontend
            logger.info(f"Generated action: {response.action}")
            
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))