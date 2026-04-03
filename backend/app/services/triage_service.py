"""
MediFlow AI - Triage Service
Hybrid rule-based + AI triage system
"""

import re
from typing import Tuple, List
from app.ai.agent import run_full_triage_pipeline
from app.ai.rag import get_rag


# ─── Rule-Based Keyword Maps ──────────────────────────────
EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "cardiac arrest", "stroke", "not breathing",
    "unconscious", "severe bleeding", "anaphylaxis", "seizure", "choking",
    "sudden numbness", "loss of consciousness", "severe allergic",
    "difficulty breathing", "coughing blood", "vomiting blood"
]

MEDIUM_KEYWORDS = [
    "fever", "high temperature", "infection", "moderate pain", "fracture",
    "broken bone", "sprain", "deep cut", "burn", "vomiting", "severe headache",
    "diarrhea", "dehydration", "urinary tract infection", "asthma attack",
    "blurred vision", "swelling"
]

NORMAL_KEYWORDS = [
    "mild", "cold", "cough", "runny nose", "sore throat", "minor cut",
    "bruise", "rash", "constipation", "minor headache", "fatigue",
    "muscle ache", "routine", "checkup", "follow-up"
]


def rule_based_triage(symptoms: str) -> Tuple[str, float]:
    """
    Rule-based triage with confidence scoring.
    Returns: (priority, confidence_score)
    """
    text = symptoms.lower()
    
    emergency_score = sum(1 for kw in EMERGENCY_KEYWORDS if kw in text)
    medium_score = sum(1 for kw in MEDIUM_KEYWORDS if kw in text)
    normal_score = sum(1 for kw in NORMAL_KEYWORDS if kw in text)

    total = emergency_score + medium_score + normal_score + 1  # +1 to avoid division by zero

    if emergency_score > 0:
        return "Emergency", round(emergency_score / total * 100, 2)
    elif medium_score > 0:
        return "Medium", round(medium_score / total * 100, 2)
    else:
        return "Normal", round(max(normal_score / total * 100, 60.0), 2)  # Default 60% for normal


def get_recommended_actions(priority: str, symptoms: str) -> List[str]:
    """Generate context-aware recommended actions."""
    base_actions = {
        "Emergency": [
            "Contact emergency services immediately",
            "Notify on-call physician",
            "Prepare emergency bay",
            "Monitor vitals continuously",
        ],
        "Medium": [
            "Schedule appointment within 2-4 hours",
            "Monitor symptoms closely",
            "Administer basic first aid if applicable",
            "Notify duty nurse",
        ],
        "Normal": [
            "Schedule routine consultation",
            "Advise patient on self-care",
            "Follow up within 24-48 hours if symptoms worsen",
        ],
    }
    actions = base_actions.get(priority, base_actions["Normal"]).copy()

    # Add symptom-specific actions
    text = symptoms.lower()
    if "chest pain" in text:
        actions.insert(0, "Run ECG immediately")
    if "fever" in text:
        actions.append("Record temperature history")
    if "breathing" in text:
        actions.insert(0, "Check oxygen saturation (SpO2)")

    return actions


def parse_llm_response(llm_output: str) -> Tuple[str, str]:
    """Parse structured LLM output to extract priority and explanation."""
    priority = "Normal"
    explanation = llm_output.strip()

    # Try to extract Priority line
    priority_match = re.search(r"Priority[:\s]+(\w+)", llm_output, re.IGNORECASE)
    if priority_match:
        extracted = priority_match.group(1).strip().capitalize()
        if extracted in ["Emergency", "Medium", "Normal"]:
            priority = extracted

    # Try to extract Explanation
    explanation_match = re.search(r"Explanation[:\s]+(.+?)(?:Recommended|$)", llm_output, re.IGNORECASE | re.DOTALL)
    if explanation_match:
        explanation = explanation_match.group(1).strip()

    return priority, explanation


def analyze_symptoms(symptoms: str) -> dict:
    """
    Main triage entry point.
    Combines rule-based + AI triage for best results.
    """
    # Step 1: Fast rule-based check
    rule_priority, rule_confidence = rule_based_triage(symptoms)

    # Step 2: If high confidence emergency or normal rule match, use that
    if rule_priority == "Emergency" and rule_confidence >= 50:
        actions = get_recommended_actions("Emergency", symptoms)
        
        # Still store in RAG for future retrieval
        rag = get_rag()
        rag.add_entry(
            patient_id=0,  # Will be updated by caller with real patient_id
            symptoms=symptoms,
            priority="Emergency",
            explanation="Rule-based: High-confidence emergency keyword match."
        )
        return {
            "priority": "Emergency",
            "explanation": "Detected critical emergency keywords. Immediate intervention required.",
            "confidence": rule_confidence,
            "recommended_actions": actions,
            "source": "rule_based",
        }

    # Step 3: Full AI pipeline for nuanced analysis
    try:
        ai_result = run_full_triage_pipeline(symptoms)
        priority, explanation = parse_llm_response(ai_result.get("explanation", ""))
        actions = get_recommended_actions(priority, symptoms)

        return {
            "priority": priority,
            "explanation": explanation,
            "confidence": None,
            "recommended_actions": actions,
            "scheduling_recommendation": ai_result.get("scheduling_recommendation"),
            "source": "ai",
        }
    except Exception as e:
        print(f"[TriageService] AI pipeline failed, using rule-based: {e}")
        actions = get_recommended_actions(rule_priority, symptoms)
        return {
            "priority": rule_priority,
            "explanation": f"Rule-based analysis: {rule_priority} priority detected.",
            "confidence": rule_confidence,
            "recommended_actions": actions,
            "source": "rule_based_fallback",
        }
