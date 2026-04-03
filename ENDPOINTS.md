# MediFlow AI - Complete Endpoint & Connection Guide

## 🚀 Quick Start

### Option 1: Using Batch Scripts (Recommended)
```bash
# First time setup
setup.bat

# Start servers
run.bat

# Or start and test
start_and_test.bat
```

### Option 2: Manual Start
```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
venv\Scripts\activate
python server.py
```

### Option 3: Test Endpoints
```bash
# After servers are running
python test_endpoints.py
```

## 📡 Complete API Reference

### Base URLs
- **Backend API**: `http://localhost:8000`
- **Frontend**: `http://localhost:5000`
- **API Docs**: `http://localhost:8000/docs` (Interactive Swagger UI)
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🔐 Authentication Endpoints

### POST /auth/register
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "role": "patient"  // patient | doctor | admin
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "patient",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### POST /auth/login
Login and receive JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "patient",
  "user_id": 1
}
```

---

### GET /auth/me
Get current user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "patient",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## 🏥 Patient Endpoints

### POST /patient/register
Create patient profile (requires authentication).

**Request:**
```json
{
  "name": "John Doe",
  "age": 30,
  "gender": "Male",
  "blood_group": "O+",
  "phone": "+1234567890",
  "address": "123 Main St",
  "medical_history": "No significant history"
}
```

**Response:** `201 Created`

---

### GET /patient/profile
Get patient's own profile.

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "John Doe",
  "age": 30,
  "gender": "Male",
  "blood_group": "O+",
  "priority": "Normal",
  "ward": null,
  "current_symptoms": "Mild headache",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### POST /patient/symptoms
Submit symptoms for AI analysis.

**Request:**
```json
{
  "symptoms": "I have chest pain and difficulty breathing"
}
```

**Response:** `200 OK`
```json
{
  "priority": "Emergency",
  "explanation": "Symptoms suggest cardiac emergency requiring immediate attention",
  "confidence": 95.5,
  "recommended_actions": [
    "Contact emergency services immediately",
    "Run ECG immediately",
    "Monitor vitals continuously"
  ]
}
```

---

### GET /patient/history
Get symptom submission history.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "symptoms": "Chest pain",
    "ai_priority": "Emergency",
    "ai_explanation": "Critical condition detected",
    "logged_at": "2024-01-01T12:00:00Z"
  }
]
```

---

### GET /patient/appointments
Get all appointments for the patient.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "patient_id": 1,
    "doctor_id": 2,
    "appointment_time": "2024-01-02T10:00:00Z",
    "status": "scheduled",
    "notes": "Follow-up visit",
    "ai_summary": null
  }
]
```

---

## 👨‍⚕️ Doctor Endpoints

### GET /doctor/patients
Get all patients (doctors and admins only).

**Query Parameters:**
- `priority` (optional): Filter by priority (Emergency/Medium/Normal)
- `limit` (optional): Max results (default: 50)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "age": 30,
    "priority": "Emergency",
    "current_symptoms": "Chest pain"
  }
]
```

---

### POST /doctor/analysis
Run AI analysis on patient notes.

**Request:**
```json
{
  "patient_id": 1,
  "notes": "Patient reports persistent chest pain for 2 hours"
}
```

**Response:** `200 OK`
```json
{
  "priority": "Emergency",
  "explanation": "Cardiac emergency suspected",
  "confidence": 92.0,
  "recommended_actions": [...]
}
```

---

### GET /doctor/schedule
Get doctor's appointment schedule.

**Query Parameters:**
- `date` (optional): Filter by date (YYYY-MM-DD format)

**Response:** `200 OK`

---

### POST /doctor/appointments
Book an appointment.

**Request:**
```json
{
  "patient_id": 1,
  "doctor_id": 2,
  "appointment_time": "2024-01-02T10:00:00Z",
  "notes": "Follow-up consultation"
}
```

**Response:** `201 Created`

---

### GET /doctor/suggest-slot
Get AI-suggested appointment slot.

**Query Parameters:**
- `priority`: Priority level (Emergency/Medium/Normal)
- `specialization` (optional): Doctor specialization

**Response:** `200 OK`
```json
{
  "suggested_time": "2024-01-01T14:30:00Z",
  "priority": "Emergency",
  "recommended_doctor": {
    "id": 2,
    "name": "Dr. Smith",
    "specialization": "Cardiology"
  },
  "slot_available": true,
  "message": "🚨 Emergency slot reserved."
}
```

---

## 🤖 AI Engine Endpoints

### POST /ai/analyze
AI-powered symptom analysis.

**Request:**
```json
{
  "symptoms": "fever and headache for 2 days"
}
```

**Response:** `200 OK`
```json
{
  "priority": "Medium",
  "explanation": "Symptoms indicate possible infection requiring prompt care",
  "confidence": 85.0,
  "recommended_actions": [
    "Schedule appointment within 2-4 hours",
    "Monitor symptoms closely",
    "Record temperature history"
  ]
}
```

---

### POST /ai/chat
AI chatbot for health queries.

**Request:**
```json
{
  "message": "What should I do for a headache?",
  "patient_id": 1  // optional, for context
}
```

**Response:** `200 OK`
```json
{
  "reply": "For headaches, ensure proper hydration and rest. Over-the-counter pain relievers like acetaminophen can help. However, if the headache is severe or persistent, please consult with a MediFlow doctor.",
  "context_used": false
}
```

---

### DELETE /ai/chat/reset
Clear chat history for current user.

**Response:** `200 OK`

---

### GET /ai/status
Check AI engine status.

**Response:** `200 OK`
```json
{
  "status": "online",
  "llm_engine": "HuggingFaceHub",
  "rag_enabled": true,
  "model": "mistralai/Mistral-7B-Instruct-v0.2",
  "message": "MediFlow AI Engine is operational."
}
```

---

## 👑 Admin Endpoints

### GET /admin/analytics
Get platform analytics (admins only).

**Response:** `200 OK`
```json
{
  "platform": "MediFlow AI",
  "summary": {
    "total_users": 150,
    "total_patients": 120,
    "total_doctors": 25,
    "total_appointments": 450
  },
  "patient_priority_distribution": {
    "Emergency": 15,
    "Medium": 45,
    "Normal": 60
  },
  "ai_accuracy": "98.4%",
  "status": "operational"
}
```

---

## 🌐 Frontend Routes

### Public Routes
- `GET /` - Landing page
- `GET /login` - Login page
- `POST /login` - Login form submission
- `GET /register` - Registration page
- `POST /register` - Registration form submission
- `GET /logout` - Logout

### Protected Routes (Require Login)
- `GET /dashboard` - Main dashboard
- `GET /appointments` - Appointments page
- `GET /ai-chat` - AI chatbot interface

### Patient-Only Routes
- `GET /symptoms` - Symptom submission page
- `POST /symptoms` - Submit symptoms
- `GET /history` - Symptom history

### Doctor/Admin Routes
- `GET /patients` - Patient management panel

### API Proxy Routes (for AJAX)
- `POST /api/chat` - Proxy to backend /ai/chat
- `POST /api/analyze` - Proxy to backend /ai/analyze
- `GET /api/status` - Check backend connectivity

---

## 🔗 Connection Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       │ HTTP
       ▼
┌─────────────────┐      HTTP/JSON      ┌──────────────────┐
│  Flask Frontend │ ──────────────────> │  FastAPI Backend │
│   (Port 5000)   │ <────────────────── │   (Port 8000)    │
└─────────────────┘                     └────────┬─────────┘
       │                                         │
       │ Templates                               │ ORM
       ▼                                         ▼
┌─────────────────┐                     ┌──────────────────┐
│  Jinja2 HTML    │                     │  SQLite Database │
└─────────────────┘                     │  (mediflow.db)   │
                                        └──────────────────┘
                                                │
                                                │ Queries
                                                ▼
                                        ┌──────────────────┐
                                        │   AI Services    │
                                        │  - Triage        │
                                        │  - RAG/FAISS     │
                                        │  - LLM (Mistral) │
                                        └──────────────────┘
```

---

## 🛠️ Environment Configuration

### Backend (.env)
```ini
DATABASE_URL=sqlite:///./mediflow.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

HUGGINGFACE_API_TOKEN=your-hf-token-here
USE_HF_API=true
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.2

EMBED_MODEL=all-MiniLM-L6-v2
FAISS_INDEX_PATH=./mediflow_faiss.index
```

### Frontend (.env)
```ini
API_BASE_URL=http://localhost:8000
FLASK_PORT=5000
FLASK_DEBUG=true
FLASK_SECRET_KEY=your-flask-secret-here
```

---

## 🧪 Testing

### Run Full Test Suite
```bash
python test_endpoints.py
```

### Manual Testing with cURL

**Register:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","role":"patient"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'
```

**Analyze Symptoms:**
```bash
curl -X POST http://localhost:8000/ai/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symptoms":"chest pain"}'
```

---

## 🔍 Troubleshooting

### Backend Won't Start
1. Check if port 8000 is already in use: `netstat -ano | findstr :8000`
2. Verify virtual environment is activated
3. Check backend.log for errors
4. Ensure all dependencies are installed: `pip install -r requirements.txt`

### Frontend Can't Connect to Backend
1. Verify backend is running on port 8000
2. Check API_BASE_URL in frontend/.env
3. Ensure CORS is enabled in backend (it is by default)
4. Test backend directly: `curl http://localhost:8000/health`

### Database Issues
1. Delete mediflow.db to reset database
2. Database auto-creates on first backend start
3. Check write permissions in backend folder

### AI/LLM Errors
1. Verify HUGGINGFACE_API_TOKEN in backend/.env
2. Set USE_HF_API=true to use inference API (no GPU needed)
3. System will fall back to rule-based triage if LLM fails

---

## 📚 Additional Resources

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **Source Code**: Check individual route files in `backend/app/routes/`
- **Database Schema**: Check `backend/app/models/`

---

## ✅ Verification Checklist

- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 5000
- [ ] Can access http://localhost:8000/docs
- [ ] Can access http://localhost:5000
- [ ] Can register a new user
- [ ] Can login and receive token
- [ ] Can submit symptoms and get AI analysis
- [ ] Database file created (mediflow.db)
- [ ] All endpoints return expected responses

---

**Last Updated**: 2024
**Version**: 1.0.0
