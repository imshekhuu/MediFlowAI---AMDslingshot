"""
MediFlow AI - LangChain Agents
Triage Agent, Doctor Assistant Agent, Scheduler Agent
"""

import os
from typing import Optional
try:
    from langchain.agents import AgentType, initialize_agent
    from langchain.tools import Tool
    from langchain.memory import ConversationBufferWindowMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    
    # Dummy classes for typing to avoid syntax errors
    class Tool:
        def __init__(self, **kwargs): pass

from app.ai.llm import get_llm, run_triage, run_chat
from app.ai.rag import get_rag


# ─── Tool Definitions ─────────────────────────────────────

def triage_tool_fn(symptoms: str) -> str:
    """Run AI triage on given symptoms."""
    return run_triage(symptoms)


def rag_lookup_fn(query: str) -> str:
    """Retrieve similar historical patient cases."""
    rag = get_rag()
    context = rag.build_context(query)
    return context if context else "No similar historical cases found."


def emergency_escalation_fn(input_str: str) -> str:
    """Determine if emergency escalation is needed."""
    emergency_keywords = [
        "chest pain", "heart attack", "cardiac arrest", "stroke",
        "unconscious", "not breathing", "severe bleeding", "anaphylaxis"
    ]
    if any(kw in input_str.lower() for kw in emergency_keywords):
        return "🚨 EMERGENCY ESCALATION: Immediately alert on-call team. Patient requires urgent care."
    return "No immediate escalation required. Proceed with standard triage protocol."


def scheduling_tool_fn(input_str: str) -> str:
    """Suggest appointment scheduling based on priority."""
    if "emergency" in input_str.lower():
        return "Schedule IMMEDIATELY: Book emergency slot within 30 minutes."
    elif "medium" in input_str.lower():
        return "Schedule URGENTLY: Book within 2-4 hours today."
    else:
        return "Schedule ROUTINE: Book within 24-48 hours. Standard queue."


# ─── Tool Registry ────────────────────────────────────────
TRIAGE_TOOLS = [
    Tool(
        name="SymptomTriageAnalyzer",
        func=triage_tool_fn,
        description=(
            "Analyzes patient symptoms and classifies urgency as Emergency, Medium, or Normal. "
            "Input: plain text description of symptoms."
        ),
    ),
    Tool(
        name="PatientHistoryRetriever",
        func=rag_lookup_fn,
        description=(
            "Retrieves similar historical patient cases from the MediFlow database "
            "using semantic search. Input: symptom description."
        ),
    ),
    Tool(
        name="EmergencyEscalation",
        func=emergency_escalation_fn,
        description=(
            "Determines if an emergency escalation alert should be triggered. "
            "Input: symptoms or triage result."
        ),
    ),
] if LANGCHAIN_AVAILABLE else []

SCHEDULER_TOOLS = [
    Tool(
        name="AppointmentScheduler",
        func=scheduling_tool_fn,
        description=(
            "Suggests appointment timing based on patient priority level. "
            "Input: priority level (Emergency/Medium/Normal)."
        ),
    ),
]


# ─── Agent Factory ────────────────────────────────────────

def get_triage_agent():
    """
    Triage Agent: analyzes symptoms, checks history, escalates if needed.
    Uses LangChain zero-shot ReAct agent.
    """
    llm = get_llm()
    # Fallback: if LLM doesn't support agents, use simple chain
    if hasattr(llm, '__class__') and llm.__class__.__name__ == 'FallbackLLM':
        class SimpleTriageAgent:
            def run(self, symptoms: str) -> str:
                triage_result = triage_tool_fn(symptoms)
                history = rag_lookup_fn(symptoms)
                escalation = emergency_escalation_fn(symptoms)
                return f"{triage_result}\n\n{history}\n\n{escalation}"
        return SimpleTriageAgent()

    try:
        if not LANGCHAIN_AVAILABLE: raise ImportError("Langchain disabled")
        memory = ConversationBufferWindowMemory(k=3, memory_key="chat_history")
        agent = initialize_agent(
            tools=TRIAGE_TOOLS,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
            max_iterations=4,
            handle_parsing_errors=True,
        )
        return agent
    except Exception as e:
        print(f"[Agent] Triage agent init failed: {e}. Using simple fallback.")
        class SimpleTriageAgent:
            def run(self, symptoms: str) -> str:
                return triage_tool_fn(symptoms)
        return SimpleTriageAgent()


def get_scheduler_agent():
    """Scheduler Agent: determines when to book appointments."""
    llm = get_llm()
    if hasattr(llm, '__class__') and llm.__class__.__name__ == 'FallbackLLM':
        class SimpleSchedulerAgent:
            def run(self, priority: str) -> str:
                return scheduling_tool_fn(priority)
        return SimpleSchedulerAgent()

    try:
        if not LANGCHAIN_AVAILABLE: raise ImportError("Langchain disabled")
        agent = initialize_agent(
            tools=SCHEDULER_TOOLS,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
            max_iterations=3,
            handle_parsing_errors=True,
        )
        return agent
    except Exception as e:
        print(f"[Agent] Scheduler agent init failed: {e}")
        class SimpleSchedulerAgent:
            def run(self, priority: str) -> str:
                return scheduling_tool_fn(priority)
        return SimpleSchedulerAgent()


def run_full_triage_pipeline(symptoms: str) -> dict:
    """
    Full triage pipeline:
    1. RAG retrieval of similar cases
    2. LLM-based triage classification
    3. Scheduling recommendation
    """
    # Step 1: Retrieve context
    rag = get_rag()
    context = rag.build_context(symptoms)

    # Step 2: Triage
    triage_result = run_triage(symptoms)

    # Step 3: Parse result
    priority = "Normal"
    explanation = triage_result
    if "Emergency" in triage_result:
        priority = "Emergency"
    elif "Medium" in triage_result:
        priority = "Medium"

    # Step 4: Schedule recommendation
    schedule_rec = scheduling_tool_fn(priority)

    return {
        "priority": priority,
        "explanation": explanation,
        "context": context,
        "scheduling_recommendation": schedule_rec,
    }
