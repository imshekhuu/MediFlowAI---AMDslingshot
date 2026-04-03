"""
MediFlow AI - LLM Integration
Hugging Face Mistral-7B via LangChain (with CPU/GPU fallback)
"""

import os
from functools import lru_cache
try:
    from langchain.llms.base import LLM
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    
    # Dummy classes for typing to avoid NameErrors
    class PromptTemplate:
        def __init__(self, **kwargs): pass
    class LLMChain:
        def __init__(self, **kwargs): pass
from typing import Optional

# ─── Environment Config ───────────────────────────────────
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
HF_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")
USE_API = os.getenv("USE_HF_API", "true").lower() == "true"  # Use API by default (lighter)


# ─── Hugging Face API (Lightweight, no GPU needed) ────────
def get_hf_api_llm():
    """Use Hugging Face Inference API (no local GPU needed)."""
    try:
        from langchain_community.llms import HuggingFaceHub
        return HuggingFaceHub(
            repo_id=HF_MODEL,
            huggingfacehub_api_token=HF_API_TOKEN,
            model_kwargs={"temperature": 0.3, "max_new_tokens": 512}
        )
    except Exception as e:
        print(f"[LLM] HF API unavailable: {e}")
        return None


# ─── Local Hugging Face Pipeline (GPU/CPU) ────────────────
def get_local_llm():
    """Load model locally via transformers pipeline."""
    try:
        from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
        import torch
        from langchain_community.llms import HuggingFacePipeline

        device = 0 if torch.cuda.is_available() else -1
        print(f"[LLM] Loading local model on {'GPU' if device == 0 else 'CPU'}...")

        tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
        model = AutoModelForCausalLM.from_pretrained(
            HF_MODEL,
            torch_dtype=torch.float16 if device == 0 else torch.float32,
            device_map="auto" if device == 0 else None,
            low_cpu_mem_usage=True,
        )
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=512,
            temperature=0.3,
            do_sample=True,
        )
        return HuggingFacePipeline(pipeline=pipe)
    except Exception as e:
        print(f"[LLM] Local model load failed: {e}")
        return None


# ─── Fallback Rule-Based LLM ─────────────────────────────
class FallbackLLM:
    """Simple rule-based fallback when no LLM is available."""
    def __call__(self, prompt: str) -> str:
        symptoms_lower = prompt.lower()
        if any(kw in symptoms_lower for kw in ["chest pain", "heart attack", "cardiac", "stroke", "unconscious", "no pulse"]):
            return "Priority: Emergency\nExplanation: Symptoms suggest a critical cardiac or neurological emergency. Immediate intervention required."
        elif any(kw in symptoms_lower for kw in ["fever", "infection", "difficulty breathing", "fracture", "severe pain"]):
            return "Priority: Medium\nExplanation: Symptoms indicate a moderate severity condition requiring prompt medical attention."
        else:
            return "Priority: Normal\nExplanation: Symptoms do not indicate immediate danger. Routine care and monitoring recommended."


@lru_cache(maxsize=1)
def get_llm():
    """Get the best available LLM (API → Local → Fallback)."""
    if USE_API and HF_API_TOKEN:
        llm = get_hf_api_llm()
        if llm:
            print("[LLM] Using HuggingFace Inference API")
            return llm

    llm = get_local_llm()
    if llm:
        print("[LLM] Using local model pipeline")
        return llm

    print("[LLM] Using rule-based fallback")
    return FallbackLLM()


# ─── Prompt Templates ─────────────────────────────────────
TRIAGE_PROMPT = PromptTemplate(
    input_variables=["symptoms"],
    template="""You are a senior medical triage AI assistant for MediFlow AI.

Analyze the following patient symptoms and classify urgency level.

Symptoms: {symptoms}

Respond in this exact format:
Priority: [Emergency / Medium / Normal]
Explanation: [Brief clinical explanation in 1-2 sentences]
Recommended Actions: [Comma-separated list of immediate actions]

Your response:"""
)

CHAT_PROMPT = PromptTemplate(
    input_variables=["history", "message"],
    template="""You are MediFlow AI, a professional medical assistant chatbot.
You help patients understand their health concerns and guide them to appropriate care.
Always recommend consulting a real doctor for diagnosis.

Conversation history:
{history}

Patient: {message}
MediFlow AI:"""
)


def run_triage(symptoms: str) -> str:
    """Run triage analysis using the LLM."""
    if not LANGCHAIN_AVAILABLE:
        return FallbackLLM()(symptoms)
        
    llm = get_llm()
    if isinstance(llm, FallbackLLM):
        return llm(symptoms)
        
    try:
        # We check again inside because get_llm could return FallbackLLM
        # but the chain initialization needs the classes.
        chain = LLMChain(llm=llm, prompt=TRIAGE_PROMPT)
        return chain.run(symptoms=symptoms)
    except Exception as e:
        print(f"[LLM] Triage error: {e}")
        return FallbackLLM()(symptoms)


def run_chat(message: str, history: str = "") -> str:
    """Run a chatbot response."""
    if not LANGCHAIN_AVAILABLE:
        return "I am MediFlow AI. I can help with general health queries. Please consult your MediFlow doctor for medical advice."

    llm = get_llm()
    if isinstance(llm, FallbackLLM):
        return "I can help with general health queries. Please consult your MediFlow doctor for medical advice. (Lite mode)"
        
    try:
        chain = LLMChain(llm=llm, prompt=CHAT_PROMPT)
        return chain.run(message=message, history=history)
    except Exception as e:
        print(f"[LLM] Chat error: {e}")
        return "I'm temporarily unavailable. Please try again or contact your care team."
