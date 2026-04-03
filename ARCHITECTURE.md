# MediFlow AI - System Architecture Diagram

## 🏗️ Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            USER LAYER (Browser)                              │
│                         http://localhost:5000                                │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 │ HTTP/HTML
                                 │ Jinja2 Templates
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                        PRESENTATION LAYER                                    │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Flask Frontend (Port 5000)                                         │    │
│  │  ├─ Public Routes: /, /login, /register                            │    │
│  │  ├─ Patient Routes: /symptoms, /history, /appointments             │    │
│  │  ├─ Doctor Routes: /patients, /schedule                            │    │
│  │  ├─ Admin Routes: /dashboard (analytics)                           │    │
│  │  └─ API Proxies: /api/chat, /api/analyze, /api/status             │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 │ HTTP/JSON + JWT Auth
                                 │ Headers: Authorization: Bearer <token>
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                          API LAYER (Backend)                                 │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  FastAPI Application (Port 8000)                                   │    │
│  │  ┌──────────────────────────────────────────────────────────────┐ │    │
│  │  │  AUTHENTICATION (/auth)                                       │ │    │
│  │  │  • POST /auth/register  - User registration                   │ │    │
│  │  │  • POST /auth/login     - JWT token generation                │ │    │
│  │  │  • GET  /auth/me        - Get current user                    │ │    │
│  │  └──────────────────────────────────────────────────────────────┘ │    │
│  │  ┌──────────────────────────────────────────────────────────────┐ │    │
│  │  │  PATIENT ROUTES (/patient)                                    │ │    │
│  │  │  • POST /patient/register     - Create profile                │ │    │
│  │  │  • POST /patient/symptoms     - Submit symptoms               │ │    │
│  │  │  • GET  /patient/history      - Get symptom logs              │ │    │
│  │  │  • GET  /patient/profile      - Get profile                   │ │    │
│  │  │  • GET  /patient/appointments - Get appointments              │ │    │
│  │  └──────────────────────────────────────────────────────────────┘ │    │
│  │  ┌──────────────────────────────────────────────────────────────┐ │    │
│  │  │  DOCTOR ROUTES (/doctor)                                      │ │    │
│  │  │  • GET  /doctor/patients      - List patients                 │ │    │
│  │  │  • POST /doctor/analysis      - AI analysis                   │ │    │
│  │  │  • GET  /doctor/schedule      - Get schedule                  │ │    │
│  │  │  • POST /doctor/appointments  - Book appointment              │ │    │
│  │  │  • GET  /doctor/suggest-slot  - AI slot suggestion            │ │    │
│  │  └──────────────────────────────────────────────────────────────┘ │    │
│  │  ┌──────────────────────────────────────────────────────────────┐ │    │
│  │  │  AI ROUTES (/ai)                                              │ │    │
│  │  │  • POST   /ai/analyze      - Symptom analysis                 │ │    │
│  │  │  • POST   /ai/chat         - Chatbot                          │ │    │
│  │  │  • DELETE /ai/chat/reset   - Clear history                    │ │    │
│  │  │  • GET    /ai/status       - Engine status                    │ │    │
│  │  └──────────────────────────────────────────────────────────────┘ │    │
│  │  ┌──────────────────────────────────────────────────────────────┐ │    │
│  │  │  ADMIN ROUTES (/admin)                                        │ │    │
│  │  │  • GET /admin/analytics - Platform statistics                 │ │    │
│  │  └──────────────────────────────────────────────────────────────┘ │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 │ ORM (SQLAlchemy)
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                          SERVICE LAYER                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Triage     │  │  Scheduler   │  │   Auth       │  │     AI       │   │
│  │   Service    │  │   Service    │  │   Utils      │  │   Services   │   │
│  │              │  │              │  │              │  │              │   │
│  │ • analyze    │  │ • create_    │  │ • hash_pwd   │  │ • LLM        │   │
│  │   symptoms   │  │   appt       │  │ • verify_pwd │  │ • RAG/FAISS  │   │
│  │ • rule-based │  │ • suggest    │  │ • create_jwt │  │ • Agents     │   │
│  │ • ai-hybrid  │  │   slot       │  │ • verify_jwt │  │ • Chat       │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 │ SQL Queries
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                         DATA LAYER (Database)                                │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  SQLite Database (mediflow.db)                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │    │
│  │  │   Users      │  │   Patients   │  │   Doctors    │            │    │
│  │  │ ─────────────│  │ ─────────────│  │ ─────────────│            │    │
│  │  │ • id         │  │ • id         │  │ • id         │            │    │
│  │  │ • email      │  │ • user_id    │  │ • user_id    │            │    │
│  │  │ • password   │  │ • name       │  │ • name       │            │    │
│  │  │ • role       │  │ • age        │  │ • special.   │            │    │
│  │  │ • is_active  │  │ • priority   │  │ • available  │            │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │    │
│  │  ┌──────────────┐  ┌──────────────┐                              │    │
│  │  │ Appointments │  │ SymptomLogs  │                              │    │
│  │  │ ─────────────│  │ ─────────────│                              │    │
│  │  │ • patient_id │  │ • patient_id │                              │    │
│  │  │ • doctor_id  │  │ • symptoms   │                              │    │
│  │  │ • time       │  │ • ai_result  │                              │    │
│  │  │ • status     │  │ • logged_at  │                              │    │
│  │  └──────────────┘  └──────────────┘                              │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI/ML LAYER (External)                               │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Hugging Face Inference API                                        │    │
│  │  • Model: mistralai/Mistral-7B-Instruct-v0.2                      │    │
│  │  • Purpose: Symptom analysis, Chat responses                      │    │
│  │  • Fallback: Rule-based triage if API unavailable                 │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  FAISS Vector Store (Optional)                                     │    │
│  │  • Model: sentence-transformers/all-MiniLM-L6-v2                  │    │
│  │  • Purpose: Retrieval Augmented Generation (RAG)                  │    │
│  │  • Storage: mediflow_faiss.index + mediflow_faiss_docs.json      │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔐 Authentication Flow

```
┌──────────┐
│  User    │
└────┬─────┘
     │ 1. POST /auth/register
     │    {email, password, role}
     ▼
┌────────────┐
│  Backend   │──► 2. Hash password (bcrypt)
└────┬───────┘    3. Store in database
     │            4. Return user object
     │
     │ 5. POST /auth/login
     │    {email, password}
     ▼
┌────────────┐
│  Backend   │──► 6. Verify password
└────┬───────┘    7. Generate JWT token
     │            8. Return {access_token, role, user_id}
     │
     ▼
┌──────────┐
│  User    │──► 9. Store token in session
└────┬─────┘    
     │ 10. All requests include:
     │     Authorization: Bearer <token>
     ▼
┌────────────┐
│  Backend   │──► 11. Verify JWT
└────┬───────┘    12. Check role permissions
     │            13. Execute request
     ▼
┌──────────┐
│  User    │◄─── 14. Return response
└──────────┘
```

## 🏥 AI Triage Flow

```
Patient enters symptoms
        │
        ▼
┌──────────────────┐
│ Frontend submits │
│ to /ai/analyze   │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────┐
│ Rule-Based Quick Check  │
│ • Check keywords        │
│ • Emergency detection   │
└────────┬────────────────┘
         │
         ├─► High Confidence Emergency ──► Return Emergency
         │
         ▼
┌─────────────────────────┐
│   AI Pipeline           │
│ 1. RAG context lookup   │
│ 2. LLM analysis         │
│ 3. Priority extraction  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Update Patient Record   │
│ • Set priority          │
│ • Log symptoms          │
│ • Store in RAG          │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Return to Frontend      │
│ • Priority level        │
│ • Explanation           │
│ • Recommended actions   │
└─────────────────────────┘
```

## 📊 Database Schema Relationships

```
┌──────────┐          1:1          ┌──────────────┐
│  User    │◄─────────────────────►│   Patient    │
│          │                        │              │
│ • id     │                        │ • user_id FK │
│ • email  │                        │ • priority   │
│ • role   │                        │ • symptoms   │
└────┬─────┘                        └──────┬───────┘
     │                                     │
     │ 1:1                                 │ 1:N
     │                                     │
     ▼                                     ▼
┌──────────────┐                  ┌──────────────┐
│   Doctor     │                  │ SymptomLog   │
│              │                  │              │
│ • user_id FK │                  │ • patient_id │
│ • special.   │                  │ • ai_result  │
└──────┬───────┘                  └──────────────┘
       │
       │ 1:N
       │
       ▼
┌────────────────┐         N:1
│  Appointment   │◄─────────────┐
│                │              │
│ • patient_id FK│              │
│ • doctor_id FK │              │
│ • time         │              │
│ • status       │              │
└────────────────┘              │
                                │
                        From Patient
```

## 🎯 Request/Response Example

```
┌─────────────────────────────────────────────────────────────┐
│ Example: Submit Symptoms                                     │
└─────────────────────────────────────────────────────────────┘

1. Frontend Form Submission:
   ┌──────────────────────────────────────────┐
   │ POST /symptoms (Flask route)             │
   │ Form Data: symptoms="chest pain"         │
   └──────────────────────────────────────────┘
                    ▼
2. Flask Proxies to Backend:
   ┌──────────────────────────────────────────┐
   │ POST http://localhost:8000/patient/      │
   │      symptoms                            │
   │ Headers: Authorization: Bearer <token>   │
   │ Body: {"symptoms": "chest pain"}         │
   └──────────────────────────────────────────┘
                    ▼
3. Backend Processes:
   ┌──────────────────────────────────────────┐
   │ • Verify JWT token                       │
   │ • Get patient from DB                    │
   │ • Run AI triage analysis                 │
   │ • Update patient priority                │
   │ • Save to symptom_logs                   │
   │ • Store in RAG vector DB                 │
   └──────────────────────────────────────────┘
                    ▼
4. Backend Response:
   ┌──────────────────────────────────────────┐
   │ {                                        │
   │   "priority": "Emergency",               │
   │   "explanation": "Critical cardiac...",  │
   │   "confidence": 95.5,                    │
   │   "recommended_actions": [...]           │
   │ }                                        │
   └──────────────────────────────────────────┘
                    ▼
5. Frontend Displays Result:
   ┌──────────────────────────────────────────┐
   │ 🚨 EMERGENCY PRIORITY                    │
   │                                          │
   │ Critical cardiac emergency detected.     │
   │                                          │
   │ Actions:                                 │
   │ • Contact emergency services             │
   │ • Run ECG immediately                    │
   │ • Monitor vitals continuously            │
   └──────────────────────────────────────────┘
```

---

**Architecture Version**: 1.0.0
**Last Updated**: 2024
