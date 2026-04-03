# 🚀 Quick Deployment Guide - Google Cloud

## Fastest Way to Deploy MediFlow AI (5 Minutes)

### Prerequisites
```bash
# Install Google Cloud SDK
# Windows: Download from https://cloud.google.com/sdk/docs/install
# Mac: brew install --cask google-cloud-sdk
# Linux: curl https://sdk.cloud.google.com | bash

# Login and setup
gcloud init
gcloud auth login
```

---

## 🎯 Quick Deploy (Copy & Paste)

### Step 1: Set Your Project
```bash
# Replace with your actual project ID
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"

gcloud config set project $PROJECT_ID
```

### Step 2: Enable APIs (One Command)
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com containerregistry.googleapis.com secretmanager.googleapis.com
```

### Step 3: Create Secrets
```bash
# JWT Secret
echo -n "$(openssl rand -base64 32)" | gcloud secrets create jwt-secret-key --data-file=-

# Flask Secret
echo -n "$(openssl rand -base64 32)" | gcloud secrets create flask-secret-key --data-file=-

# Hugging Face Token (replace YOUR_TOKEN)
echo -n "YOUR_HF_TOKEN_HERE" | gcloud secrets create huggingface-token --data-file=-
```

### Step 4: Deploy Backend
```bash
cd backend

# Build & Deploy in one command
gcloud run deploy mediflow-backend \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --set-env-vars "APP_ENV=production,USE_HF_API=true,DATABASE_URL=sqlite:////tmp/mediflow.db" \
  --set-secrets "SECRET_KEY=jwt-secret-key:latest,HUGGINGFACE_API_TOKEN=huggingface-token:latest"

cd ..
```

### Step 5: Get Backend URL
```bash
BACKEND_URL=$(gcloud run services describe mediflow-backend --region $REGION --format 'value(status.url)')
echo "Backend URL: $BACKEND_URL"
```

### Step 6: Deploy Frontend
```bash
cd frontend

# Deploy with backend URL
gcloud run deploy mediflow-frontend \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --set-env-vars "API_BASE_URL=$BACKEND_URL,FLASK_DEBUG=false" \
  --set-secrets "FLASK_SECRET_KEY=flask-secret-key:latest"

cd ..
```

### Step 7: Get Frontend URL & Test
```bash
FRONTEND_URL=$(gcloud run services describe mediflow-frontend --region $REGION --format 'value(status.url)')
echo "✅ Deployment Complete!"
echo "Frontend: $FRONTEND_URL"
echo "Backend: $BACKEND_URL"

# Open in browser
open $FRONTEND_URL  # Mac
start $FRONTEND_URL  # Windows
```

---

## 📝 All Commands in One Script

### For Linux/Mac (Bash)
```bash
#!/bin/bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export HF_TOKEN="your-hf-token"

gcloud config set project $PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com

echo -n "$(openssl rand -base64 32)" | gcloud secrets create jwt-secret-key --data-file=-
echo -n "$(openssl rand -base64 32)" | gcloud secrets create flask-secret-key --data-file=-
echo -n "$HF_TOKEN" | gcloud secrets create huggingface-token --data-file=-

cd backend
gcloud run deploy mediflow-backend --source . --platform managed --region $REGION \
  --allow-unauthenticated --port 8080 --memory 2Gi \
  --set-env-vars "APP_ENV=production,USE_HF_API=true,DATABASE_URL=sqlite:////tmp/mediflow.db" \
  --set-secrets "SECRET_KEY=jwt-secret-key:latest,HUGGINGFACE_API_TOKEN=huggingface-token:latest"
cd ..

BACKEND_URL=$(gcloud run services describe mediflow-backend --region $REGION --format 'value(status.url)')

cd frontend
gcloud run deploy mediflow-frontend --source . --platform managed --region $REGION \
  --allow-unauthenticated --port 8080 --memory 512Mi \
  --set-env-vars "API_BASE_URL=$BACKEND_URL,FLASK_DEBUG=false" \
  --set-secrets "FLASK_SECRET_KEY=flask-secret-key:latest"
cd ..

FRONTEND_URL=$(gcloud run services describe mediflow-frontend --region $REGION --format 'value(status.url)')
echo "✅ Frontend: $FRONTEND_URL"
echo "✅ Backend: $BACKEND_URL"
```

### For Windows (PowerShell)
```powershell
$PROJECT_ID = "your-project-id"
$REGION = "us-central1"
$HF_TOKEN = "your-hf-token"

gcloud config set project $PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com

# Create secrets
$jwt = -join ((65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
echo $jwt | gcloud secrets create jwt-secret-key --data-file=-

$flask = -join ((65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
echo $flask | gcloud secrets create flask-secret-key --data-file=-

echo $HF_TOKEN | gcloud secrets create huggingface-token --data-file=-

# Deploy backend
cd backend
gcloud run deploy mediflow-backend --source . --platform managed --region $REGION `
  --allow-unauthenticated --port 8080 --memory 2Gi `
  --set-env-vars "APP_ENV=production,USE_HF_API=true,DATABASE_URL=sqlite:////tmp/mediflow.db" `
  --set-secrets "SECRET_KEY=jwt-secret-key:latest,HUGGINGFACE_API_TOKEN=huggingface-token:latest"
cd ..

# Get backend URL
$BACKEND_URL = gcloud run services describe mediflow-backend --region $REGION --format "value(status.url)"

# Deploy frontend
cd frontend
gcloud run deploy mediflow-frontend --source . --platform managed --region $REGION `
  --allow-unauthenticated --port 8080 --memory 512Mi `
  --set-env-vars "API_BASE_URL=$BACKEND_URL,FLASK_DEBUG=false" `
  --set-secrets "FLASK_SECRET_KEY=flask-secret-key:latest"
cd ..

# Get frontend URL
$FRONTEND_URL = gcloud run services describe mediflow-frontend --region $REGION --format "value(status.url)"

Write-Host "✅ Frontend: $FRONTEND_URL"
Write-Host "✅ Backend: $BACKEND_URL"
```

---

## 🔄 Update/Redeploy

### Redeploy Backend Only
```bash
cd backend
gcloud run deploy mediflow-backend --source . --region $REGION
cd ..
```

### Redeploy Frontend Only
```bash
cd frontend
gcloud run deploy mediflow-frontend --source . --region $REGION
cd ..
```

### Update Environment Variables
```bash
# Backend
gcloud run services update mediflow-backend --region $REGION \
  --update-env-vars "NEW_VAR=value"

# Frontend
gcloud run services update mediflow-frontend --region $REGION \
  --update-env-vars "NEW_VAR=value"
```

---

## 🧹 Clean Up / Delete Everything

```bash
# Delete services
gcloud run services delete mediflow-backend --region $REGION --quiet
gcloud run services delete mediflow-frontend --region $REGION --quiet

# Delete secrets
gcloud secrets delete jwt-secret-key --quiet
gcloud secrets delete flask-secret-key --quiet
gcloud secrets delete huggingface-token --quiet

# Delete images
gcloud container images delete gcr.io/$PROJECT_ID/mediflow-backend --quiet
gcloud container images delete gcr.io/$PROJECT_ID/mediflow-frontend --quiet
```

---

## 💰 Cost Control

### Set to Zero Cost (Dev Mode)
```bash
# Scale down to 0 when not in use
gcloud run services update mediflow-backend --region $REGION --min-instances 0
gcloud run services update mediflow-frontend --region $REGION --min-instances 0
```

### Production Mode
```bash
# Keep 1 instance always ready
gcloud run services update mediflow-backend --region $REGION --min-instances 1 --max-instances 10
gcloud run services update mediflow-frontend --region $REGION --min-instances 1 --max-instances 5
```

---

## 🔍 Useful Commands

### View Logs
```bash
# Backend logs
gcloud run services logs read mediflow-backend --region $REGION --limit 100

# Frontend logs
gcloud run services logs read mediflow-frontend --region $REGION --limit 100

# Follow logs in real-time
gcloud run services logs tail mediflow-backend --region $REGION
```

### Check Service Status
```bash
# List all services
gcloud run services list --region $REGION

# Describe service
gcloud run services describe mediflow-backend --region $REGION

# Get URL
gcloud run services describe mediflow-backend --region $REGION --format 'value(status.url)'
```

### Test Endpoints
```bash
BACKEND_URL=$(gcloud run services describe mediflow-backend --region $REGION --format 'value(status.url)')

# Health check
curl $BACKEND_URL/health

# Test registration
curl -X POST $BACKEND_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","role":"patient"}'
```

---

## 🎯 Regions to Choose

**Americas:**
- `us-central1` (Iowa) - Cheapest
- `us-east1` (South Carolina)
- `us-west1` (Oregon)

**Europe:**
- `europe-west1` (Belgium)
- `europe-west4` (Netherlands)

**Asia:**
- `asia-south1` (Mumbai) - Good for India
- `asia-southeast1` (Singapore)
- `asia-northeast1` (Tokyo)

**Choose closest to your users for lowest latency**

---

## ✅ Verification Checklist

After deployment, verify:

```bash
# 1. Health checks
curl $BACKEND_URL/health
# Should return: {"status": "healthy", ...}

# 2. API docs
open $BACKEND_URL/docs

# 3. Frontend loads
curl $FRONTEND_URL
# Should return HTML

# 4. Frontend can reach backend
curl $FRONTEND_URL/api/status
# Should show backend status

# 5. Register test user
curl -X POST $BACKEND_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","role":"patient"}'

# 6. Login
curl -X POST $BACKEND_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
# Should return JWT token
```

---

## 🆘 Common Issues

### Issue: Permission Denied
```bash
# Solution: Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com
```

### Issue: Secret not found
```bash
# Solution: Recreate secret
gcloud secrets delete SECRET_NAME
echo -n "new-value" | gcloud secrets create SECRET_NAME --data-file=-
```

### Issue: Build timeout
```bash
# Solution: Increase timeout
gcloud builds submit --timeout=20m --tag gcr.io/$PROJECT_ID/image
```

### Issue: Out of memory
```bash
# Solution: Increase memory
gcloud run services update SERVICE_NAME --memory 4Gi
```

---

## 📊 Monitoring Dashboard

View in Cloud Console:
```
https://console.cloud.google.com/run?project=YOUR_PROJECT_ID
```

Quick metrics:
```bash
# Request count
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_count"'

# Latency
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_latencies"'
```

---

## 🎉 That's It!

Your MediFlow AI is now live on Google Cloud!

**Deployment time: ~5-10 minutes**
**Monthly cost: ~$15-35 (low traffic)**

For detailed guide, see: `DEPLOYMENT.md`
