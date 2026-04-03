"""
MediFlow AI - Patient Routes
POST /patient/register
POST /patient/symptoms
GET  /patient/history
GET  /patient/appointments
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.models.patient import Patient, SymptomLog
from app.schemas.patient_schema import (
    PatientCreate,
    SymptomInput,
    PatientResponse,
    SymptomLogResponse,
    AIAnalyzeResponse,
    AppointmentResponse,
)
from app.utils.auth_utils import get_current_user
from app.services.triage_service import analyze_symptoms
from app.ai.rag import get_rag

router = APIRouter(prefix="/patient", tags=["Patient"])


def _get_patient_or_404(db: Session, user_id: int) -> Patient:
    patient = db.query(Patient).filter(Patient.user_id == user_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found. Please register first."
        )
    return patient


@router.post("/register", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def register_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a patient profile linked to the current user account."""
    existing = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient profile already exists for this account."
        )

    patient = Patient(
        user_id=current_user.id,
        name=payload.name,
        age=payload.age,
        gender=payload.gender,
        blood_group=payload.blood_group,
        phone=payload.phone,
        address=payload.address,
        medical_history=payload.medical_history,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.post("/symptoms", response_model=AIAnalyzeResponse)
def submit_symptoms(
    payload: SymptomInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit patient symptoms → AI triage analysis → Update priority → Return result.
    """
    patient = _get_patient_or_404(db, current_user.id)

    # Run AI triage
    result = analyze_symptoms(payload.symptoms)
    priority = result["priority"]
    explanation = result["explanation"]
    actions = result.get("recommended_actions", [])

    # Update patient profile
    patient.current_symptoms = payload.symptoms
    patient.priority = priority
    db.commit()

    # Log to DB
    log = SymptomLog(
        patient_id=patient.id,
        symptoms=payload.symptoms,
        ai_priority=priority,
        ai_explanation=explanation,
    )
    db.add(log)
    db.commit()

    # Store in RAG vector store for future retrieval
    rag = get_rag()
    rag.add_entry(
        patient_id=patient.id,
        symptoms=payload.symptoms,
        priority=priority,
        explanation=explanation,
    )

    return AIAnalyzeResponse(
        priority=priority,
        explanation=explanation,
        confidence=result.get("confidence"),
        recommended_actions=actions,
    )


@router.get("/history", response_model=List[SymptomLogResponse])
def get_patient_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve the full symptom history for the logged-in patient."""
    patient = _get_patient_or_404(db, current_user.id)
    return patient.symptom_logs


@router.get("/profile", response_model=PatientResponse)
def get_patient_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the patient's own profile."""
    return _get_patient_or_404(db, current_user.id)


@router.get("/appointments", response_model=List[AppointmentResponse])
def get_my_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all appointments for the logged-in patient."""
    from app.services.scheduler_service import get_patient_appointments
    patient = _get_patient_or_404(db, current_user.id)
    return get_patient_appointments(db, patient.id)
