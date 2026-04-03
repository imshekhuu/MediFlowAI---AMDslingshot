"""
MediFlow AI - AI Routes
POST /ai/analyze
POST /ai/chat
GET  /ai/status
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.models.user import User
from app.schemas.patient_schema import (
    AIAnalyzeRequest,
    AIAnalyzeResponse,
    ChatRequest,
    ChatResponse,
)
from app.utils.auth_utils import get_current_user
from app.services.triage_service import analyze_symptoms
from app.ai.llm import run_chat
from app.ai.rag import get_rag

router = APIRouter(prefix="/ai", tags=["AI Engine"])

# In-memory chat history per user (for demo; use Redis in production)
_chat_histories: dict = {}


@router.post("/analyze", response_model=AIAnalyzeResponse)
def analyze_symptoms_endpoint(
    payload: AIAnalyzeRequest,
    current_user: User = Depends(get_current_user),
):
    """
    AI-powered symptom analysis.
    Uses hybrid rule-based + LLM triage pipeline.
    
    Example:
    POST /ai/analyze
    { "symptoms": "chest pain and dizziness" }
    → { "priority": "Emergency", "explanation": "..." }
    """
    if not payload.symptoms.strip():
        raise HTTPException(status_code=400, detail="Symptoms cannot be empty.")

    result = analyze_symptoms(payload.symptoms)
    return AIAnalyzeResponse(
        priority=result["priority"],
        explanation=result["explanation"],
        confidence=result.get("confidence"),
        recommended_actions=result.get("recommended_actions", []),
    )


@router.post("/chat", response_model=ChatResponse)
def ai_chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    MediFlow AI chatbot endpoint.
    Maintains per-user conversation history and optionally retrieves
    patient context from RAG for augmented responses.
    """
    user_id = current_user.id
    history = _chat_histories.get(user_id, "")

    # Augment with RAG context if patient context requested
    context_used = False
    if payload.patient_id:
        rag = get_rag()
        context = rag.build_context(payload.message)
        if context:
            augmented_message = f"{payload.message}\n\nContext:\n{context}"
            context_used = True
        else:
            augmented_message = payload.message
    else:
        augmented_message = payload.message

    reply = run_chat(augmented_message, history=history)

    # Update conversation history (keep last 5 turns)
    history_lines = history.split("\n")
    history_lines.append(f"Patient: {payload.message}")
    history_lines.append(f"MediFlow AI: {reply}")
    _chat_histories[user_id] = "\n".join(history_lines[-10:])  # Last 5 exchanges

    return ChatResponse(reply=reply, context_used=context_used)


@router.delete("/chat/reset")
def reset_chat_history(current_user: User = Depends(get_current_user)):
    """Clear the conversation history for the current user."""
    _chat_histories.pop(current_user.id, None)
    return {"message": "Chat history cleared."}


@router.get("/status")
def ai_status():
    """Check the AI engine status and available components."""
    from app.ai.llm import get_llm
    from app.ai.rag import FAISS_AVAILABLE

    llm = get_llm()
    llm_type = llm.__class__.__name__

    return {
        "status": "online",
        "llm_engine": llm_type,
        "rag_enabled": FAISS_AVAILABLE,
        "model": "mistralai/Mistral-7B-Instruct-v0.2" if llm_type != "FallbackLLM" else "rule-based-fallback",
        "message": "MediFlow AI Engine is operational.",
    }
