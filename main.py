# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os

# Import your existing agent
from agent.src.ai.governance_chatbot import DAOAgent

app = FastAPI()

# CORS middleware
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
    text: str

class ChatResponse(BaseModel):
    text: str

@app.post("/poke")
async def chat(request: ChatRequest):
    try:
        response = await agent.chat(request.text)
        return ChatResponse(text=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    uvicorn.run(app, host="0.0.0.0", port=port)