"""
Chatbot API route with conversation memory.
Maintains per-session chat history for context-aware responses.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from backend.services.chatbot_agent import fraud_agent

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])

# In-memory session storage (use Redis in production)
_chat_sessions: Dict[str, List[Dict]] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    answer: str
    sub_queries: list[str]
    is_greeting: bool = False


@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    try:
        # Get or create session history
        if request.session_id not in _chat_sessions:
            _chat_sessions[request.session_id] = []

        history = _chat_sessions[request.session_id]

        # Run the LangGraph agent with memory
        result = await fraud_agent.ainvoke({
            "query": request.message,
            "context": [],
            "chat_history": history,
            "is_greeting": False,
            "sub_queries": [],
            "answer": "",
        })

        # Save to conversation memory
        history.append({"role": "user", "content": request.message})
        history.append({"role": "assistant", "content": result["answer"]})

        # Keep only last 20 messages to prevent memory overflow
        if len(history) > 20:
            _chat_sessions[request.session_id] = history[-20:]

        return {
            "answer": result["answer"],
            "sub_queries": result.get("sub_queries", []),
            "is_greeting": result.get("is_greeting", False),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """Clear conversation history for a session."""
    _chat_sessions.pop(session_id, None)
    return {"status": "cleared"}
