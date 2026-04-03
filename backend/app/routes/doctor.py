"""
MediFlow AI - Doctor Routes
GET  /doctor/patients
POST /doctor/analysis
GET  /doctor/schedule
POST /doctor/appointments
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.models.user import User
from app.models.doctor import Doctor, Appointment
from app.models.patient import Patient
from app.schemas.patient_schema import (
    PatientResponse,
    DoctorAnalysisRequest,
    AIAnalyzeResponse,
    AppointmentCreate,
    AppointmentResponse,
)
from app.utils.auth_utils import get_current_user, require_role
from app.services.triage_service import analyze_symptoms
from app.services.scheduler_service import (
    create_appointment,
    get_doctor_schedule,
    suggest_appointment_slot,
)

router = APIRouter(prefix="/doctor", tags=["Doctor"])


def _get_doctor_or_404(db: Session, user_id: int) -> Doctor:
    doctor = db.query(Doctor).filter(Doctor.user_id == user_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found."
        )
    return doctor


@router.get("/patients", response_model=List[PatientResponse])
def get_all_patients(
    priority: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor", "admin")),
):
    """Get all patients, optionally filtered by priority."""
    query = db.query(Patient)
    if priority:
        query = query.filter(Patient.priority == priority)
    return query.order_by(Patient.priority).limit(limit).all()


@router.post("/analysis", response_model=AIAnalyzeResponse)
def run_doctor_analysis(
    payload: DoctorAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor", "admin")),
):
    """
    Doctor submits clinical notes for AI analysis.
    Updates patient priority and generates AI recommendation.
    """
    patient = db.query(Patient).filter(Patient.id == payload.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")

    result = analyze_symptoms(payload.notes)
    priority = result["priority"]

    # Update patient record
    patient.priority = priority
    db.commit()

    return AIAnalyzeResponse(
        priority=priority,
        explanation=result["explanation"],
        confidence=result.get("confidence"),
        recommended_actions=result.get("recommended_actions", []),
    )


@router.get("/schedule", response_model=List[AppointmentResponse])
def get_my_schedule(
    date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor", "admin")),
):
    """Get the doctor's schedule, optionally filtered by date (YYYY-MM-DD)."""
    doctor = _get_doctor_or_404(db, current_user.id)
    parsed_date = None
    if date:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    return get_doctor_schedule(db, doctor.id, parsed_date)


@router.post("/appointments", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor", "admin")),
):
    """Book an appointment for a patient."""
    appointment = create_appointment(
        db=db,
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        appointment_time=payload.appointment_time,
        notes=payload.notes,
    )
    return appointment


@router.get("/suggest-slot")
def suggest_slot(
    priority: str = "Normal",
    specialization: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor", "admin")),
):
    """Get AI-suggested appointment slot based on priority."""
    return suggest_appointment_slot(db, priority, specialization)
