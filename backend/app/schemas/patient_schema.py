"""
MediFlow AI - Patient Pydantic Schemas
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ─── Patient Registration ─────────────────────────────────
class PatientCreate(BaseModel):
    name: str
    age: int
    gender: Optional[str] = "Unknown"
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    medical_history: Optional[str] = None


# ─── Symptom Submission ───────────────────────────────────
class SymptomInput(BaseModel):
    symptoms: str


# ─── Symptom Log Response ─────────────────────────────────
class SymptomLogResponse(BaseModel):
    id: int
    symptoms: str
    ai_priority: Optional[str] = None
    ai_explanation: Optional[str] = None
    logged_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Patient Response ────────────────────────────────────
class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: Optional[str]
    blood_group: Optional[str]
    priority: Optional[str]
    ward: Optional[str]
    current_symptoms: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ─── AI Analysis Request ─────────────────────────────────
class AIAnalyzeRequest(BaseModel):
    symptoms: str


# ─── AI Analysis Response ────────────────────────────────
class AIAnalyzeResponse(BaseModel):
    priority: str
    explanation: str
    confidence: Optional[float] = None
    recommended_actions: Optional[List[str]] = None


# ─── Doctor Analysis Request ─────────────────────────────
class DoctorAnalysisRequest(BaseModel):
    patient_id: int
    notes: str


# ─── Appointment Create ──────────────────────────────────
class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_time: datetime
    notes: Optional[str] = None


# ─── Appointment Response ────────────────────────────────
class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_time: datetime
    status: str
    notes: Optional[str]
    ai_summary: Optional[str]

    class Config:
        from_attributes = True


# ─── Chat Request/Response ───────────────────────────────
class ChatRequest(BaseModel):
    message: str
    patient_id: Optional[int] = None


class ChatResponse(BaseModel):
    reply: str
    context_used: Optional[bool] = False
