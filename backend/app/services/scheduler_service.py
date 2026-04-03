"""
MediFlow AI - Scheduler Service
AI-assisted appointment scheduling and load balancing
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.doctor import Doctor, Appointment
from app.models.patient import Patient


def get_available_doctors(
    db: Session,
    specialization: Optional[str] = None
) -> List[Doctor]:
    """Get available doctors, optionally filtered by specialization."""
    query = db.query(Doctor).filter(Doctor.is_available == True)
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))
    return query.all()


def get_doctor_workload(db: Session, doctor_id: int, date: datetime) -> int:
    """Count appointments for a doctor on a given day."""
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    return (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_time >= start_of_day,
            Appointment.appointment_time < end_of_day,
            Appointment.status == "scheduled",
        )
        .count()
    )


def suggest_appointment_slot(
    db: Session,
    priority: str,
    specialization: Optional[str] = None
) -> dict:
    """
    Suggest the best appointment time and doctor based on priority.
    Emergency → soonest available (within 1h)
    Medium → within 4 hours
    Normal → next available slot (next day)
    """
    now = datetime.utcnow()
    
    time_offsets = {
        "Emergency": timedelta(minutes=30),
        "Medium": timedelta(hours=3),
        "Normal": timedelta(hours=24),
    }

    suggested_time = now + time_offsets.get(priority, timedelta(hours=24))

    # Find least-loaded doctor
    doctors = get_available_doctors(db, specialization)
    best_doctor = None
    min_load = float("inf")

    for doctor in doctors:
        load = get_doctor_workload(db, doctor.id, suggested_time)
        if load < min_load:
            min_load = load
            best_doctor = doctor

    return {
        "suggested_time": suggested_time.isoformat(),
        "priority": priority,
        "recommended_doctor": {
            "id": best_doctor.id if best_doctor else None,
            "name": best_doctor.name if best_doctor else "Auto-assigned",
            "specialization": best_doctor.specialization if best_doctor else specialization,
        } if best_doctor else None,
        "slot_available": True,
        "message": (
            "🚨 Emergency slot reserved." if priority == "Emergency"
            else "⏱️ Priority slot available." if priority == "Medium"
            else "📅 Standard slot available."
        ),
    }


def create_appointment(
    db: Session,
    patient_id: int,
    doctor_id: int,
    appointment_time: datetime,
    notes: Optional[str] = None,
    ai_summary: Optional[str] = None
) -> Appointment:
    """Create and persist a new appointment."""
    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_time=appointment_time,
        notes=notes,
        ai_summary=ai_summary,
        status="scheduled",
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_patient_appointments(db: Session, patient_id: int) -> List[Appointment]:
    """Get all appointments for a patient, ordered by time."""
    return (
        db.query(Appointment)
        .filter(Appointment.patient_id == patient_id)
        .order_by(Appointment.appointment_time.desc())
        .all()
    )


def get_doctor_schedule(db: Session, doctor_id: int, date: Optional[datetime] = None) -> List[Appointment]:
    """Get all scheduled appointments for a doctor."""
    query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status == "scheduled",
    )
    if date:
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        query = query.filter(
            Appointment.appointment_time >= start,
            Appointment.appointment_time < end,
        )
    return query.order_by(Appointment.appointment_time).all()
