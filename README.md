# 🚀 MediFlow AI — Smart Healthcare Management System

An AI-powered healthcare platform that intelligently manages patients, assists doctors, and optimizes hospital workflows using LLMs, ML, and real-time analytics.

---

## 🌐 Live Demo

Frontend: https://mediflow-frontend-373566149252.asia-south1.run.app  
API Docs: https://mediflow-backend-373566149252.asia-south1.run.app/docs  

---

## 🧠 Problem Statement

Hospitals and clinics face:
- Long patient wait times  
- Poor prioritization of critical cases  
- Manual workflows  
- Lack of AI-driven insights  

---

## 💡 Solution — MediFlow AI

MediFlow AI acts as a digital hospital brain that:
- Prioritizes patients using AI triage  
- Assists doctors with AI insights  
- Enables smart scheduling  
- Provides real-time analytics  

---

## ✨ Key Features

- AI Patient Triage (Emergency / Medium / Normal)
- Doctor Dashboard with AI Insights  
- AI Chatbot for symptom analysis  
- Real-time analytics dashboard  
- Smart appointment system  
- RAG-based patient history search  

---

## 🏗️ Tech Stack

Frontend: Next.js, Tailwind CSS  
Backend: FastAPI, SQLAlchemy  
AI/ML: Hugging Face, LangChain, FAISS  
Cloud: Google Cloud Run, Firestore / Cloud SQL  

---

## 🚀 Getting Started

### Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

### Frontend
cd frontend
npm install
npm run dev

---

## 🐳 Docker

docker-compose up --build

---

## ☁️ Deployment

gcloud builds submit --tag gcr.io/PROJECT_ID/mediflow  
gcloud run deploy mediflow --platform managed --region asia-south1 --allow-unauthenticated  

---

## 🏆 Hackathon Highlights

- AI-first architecture  
- Real-time decision making  
- Cloud-native deployment  
- Scalable design  

---

## ❤️ Final Note

MediFlow AI is a scalable AI healthcare product ready for real-world deployment.
