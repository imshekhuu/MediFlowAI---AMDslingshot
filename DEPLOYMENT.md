# 🚀 MediFlow AI - Google Cloud Deployment Guide

## Complete step-by-step guide to deploy both Backend and Frontend to Google Cloud

---

## 📋 Prerequisites

### 1. Google Cloud Account
- Sign up at https://cloud.google.com/
- Enable billing (Free tier available with $300 credit)
- Create a new project or use existing one

### 2. Install Google Cloud SDK
**Windows:**
```bash
# Download from: https://cloud.google.com/sdk/docs/install
# Or use PowerShell:
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

**Mac/Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### 3. Initialize gcloud
```bash
gcloud init
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 4. Install Docker (for local testing)
- Windows/Mac: Download from https://www.docker.com/products/docker-desktop
- Linux: `sudo apt-get install docker.io`

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Google Cloud Platform                    │
│                                                              │
│  ┌────────────────────┐         ┌────────────────────┐     │
│  │  Cloud Run         │         │  Cloud Run         │     │
│  │  (Frontend)        │◄────────│  (Backend)         │     │
│  │  Port 8080         │         │  Port 8080         │     │
│  └────────┬───────────┘         └────────┬───────────┘     │
│           │                              │                  │
│           │                              │                  │
│           │                    ┌─────────▼──────────┐      │
│           │                    │  Cloud SQL         │      │
│           │                    │  (PostgreSQL)      │      │
│           │                    └────────────────────┘      │
│           │                              │                  │
│           │                    ┌─────────▼──────────┐      │
│           │                    │  Secret Manager    │      │
│           │                    │  • JWT Keys        │      │
│           │                    │  • HF Token        │      │
│           │                    │  • DB Password     │      │
│           │                    └────────────────────┘      │
│           │                                                 │
│           │                    ┌────────────────────┐      │
│           └────────────────────│  Cloud Storage     │      │
│                                │  (Optional)        │      │
│                                │  • Static files    │      │
│                                │  • FAISS index     │      │
│                                └────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Deployment Options

### **Option 1: Automated Deployment (Recommended)**
Use provided scripts for quick deployment.

### **Option 2: Manual Deployment**
Step-by-step manual deployment with full control.

### **Option 3: CI/CD with Cloud Build**
Automated deployment on every git push.

---

## 🚀 OPTION 1: Automated Deployment (Easiest)

### Step 1: Prepare Your Project

1. **Update Configuration Files**

Edit `deploy-backend.sh`:
```bash
PROJECT_ID="your-gcp-project-id"  # e.g., "mediflow-prod-12345"
REGION="us-central1"               # Choose: us-central1, asia-south1, europe-west1
```

Edit `deploy-frontend.sh`:
```bash
PROJECT_ID="your-gcp-project-id"
REGION="us-central1"
BACKEND_URL="https://mediflow-backend-XXXXX.run.app"  # Will update after backend deploy
```

2. **Get Hugging Face API Token**
- Go to https://huggingface.co/settings/tokens
- Create a new token (read access)
- Save it for later use

### Step 2: Deploy Backend

```bash
# Make scripts executable (Linux/Mac)
chmod +x deploy-backend.sh deploy-frontend.sh

# Deploy backend
./deploy-backend.sh
```

**What it does:**
- ✅ Enables required Google Cloud APIs
- ✅ Builds Docker image
- ✅ Creates secrets in Secret Manager
- ✅ Deploys to Cloud Run
- ✅ Returns backend URL

**Expected Output:**
```
✓ Backend Deployment Complete!
Service URL:    https://mediflow-backend-abc123.run.app
API Docs:       https://mediflow-backend-abc123.run.app/docs
```

### Step 3: Update Frontend Configuration

Edit `deploy-frontend.sh` with your backend URL:
```bash
BACKEND_URL="https://mediflow-backend-abc123.run.app"
```

### Step 4: Deploy Frontend

```bash
./deploy-frontend.sh
```

**Expected Output:**
```
✓ Frontend Deployment Complete!
Frontend URL:   https://mediflow-frontend-xyz789.run.app
```

### Step 5: Test Your Deployment

Visit your frontend URL and:
1. Register a new account
2. Submit symptoms
3. Check AI analysis works

---

## 🔧 OPTION 2: Manual Step-by-Step Deployment

### BACKEND DEPLOYMENT

#### 1. Set Up Google Cloud Project

```bash
# Set your project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable APIs
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com
```

#### 2. Create Secrets

```bash
# Generate JWT secret
JWT_SECRET=$(openssl rand -base64 32)

# Create secret
echo -n "$JWT_SECRET" | gcloud secrets create jwt-secret-key \
    --data-file=- \
    --replication-policy="automatic"

# Add Hugging Face token
echo -n "YOUR_HF_TOKEN" | gcloud secrets create huggingface-token \
    --data-file=- \
    --replication-policy="automatic"
```

#### 3. Build and Push Backend Image

```bash
cd backend

# Build with Cloud Build
gcloud builds submit --tag gcr.io/$PROJECT_ID/mediflow-backend:latest

# Or build locally and push
docker build -t gcr.io/$PROJECT_ID/mediflow-backend:latest .
docker push gcr.io/$PROJECT_ID/mediflow-backend:latest
```

#### 4. Deploy Backend to Cloud Run

```bash
gcloud run deploy mediflow-backend \
    --image gcr.io/$PROJECT_ID/mediflow-backend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 1 \
    --max-instances 10 \
    --timeout 300 \
    --set-env-vars "APP_ENV=production,USE_HF_API=true,ALGORITHM=HS256,DATABASE_URL=sqlite:////tmp/mediflow.db" \
    --set-secrets "SECRET_KEY=jwt-secret-key:latest,HUGGINGFACE_API_TOKEN=huggingface-token:latest"
```

#### 5. Get Backend URL

```bash
gcloud run services describe mediflow-backend \
    --region us-central1 \
    --format 'value(status.url)'
```

Save this URL - you'll need it for frontend!

### FRONTEND DEPLOYMENT

#### 1. Create Flask Secret

```bash
FLASK_SECRET=$(openssl rand -base64 32)
echo -n "$FLASK_SECRET" | gcloud secrets create flask-secret-key \
    --data-file=- \
    --replication-policy="automatic"
```

#### 2. Build and Push Frontend Image

```bash
cd frontend

gcloud builds submit --tag gcr.io/$PROJECT_ID/mediflow-frontend:latest
```

#### 3. Deploy Frontend to Cloud Run

```bash
# Replace BACKEND_URL with your actual backend URL
BACKEND_URL="https://mediflow-backend-XXXXX.run.app"

gcloud run deploy mediflow-frontend \
    --image gcr.io/$PROJECT_ID/mediflow-frontend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 1 \
    --max-instances 5 \
    --timeout 300 \
    --set-env-vars "API_BASE_URL=$BACKEND_URL,FLASK_DEBUG=false" \
    --set-secrets "FLASK_SECRET_KEY=flask-secret-key:latest"
```

---

## 🗄️ OPTION 3: Set Up Cloud SQL (Production Database)

### Why Cloud SQL?
SQLite works for development but Cloud SQL (PostgreSQL) is needed for production:
- ✅ Persistent storage
- ✅ Better performance
- ✅ Automatic backups
- ✅ High availability

### Step 1: Create Cloud SQL Instance

```bash
# Create PostgreSQL instance
gcloud sql instances create mediflow-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=SECURE_PASSWORD_HERE \
    --backup \
    --backup-start-time=03:00

# Create database
gcloud sql databases create mediflow_production \
    --instance=mediflow-db
```

### Step 2: Create Database User

```bash
gcloud sql users create mediflow_user \
    --instance=mediflow-db \
    --password=SECURE_USER_PASSWORD
```

### Step 3: Update Backend to Use Cloud SQL

```bash
# Get connection name
gcloud sql instances describe mediflow-db \
    --format='value(connectionName)'
# Output: your-project:us-central1:mediflow-db

# Update backend deployment
gcloud run services update mediflow-backend \
    --region us-central1 \
    --add-cloudsql-instances your-project:us-central1:mediflow-db \
    --update-env-vars DATABASE_URL="postgresql://mediflow_user:SECURE_USER_PASSWORD@/mediflow_production?host=/cloudsql/your-project:us-central1:mediflow-db"
```

### Step 4: Run Database Migrations

```bash
# Connect to Cloud SQL
gcloud sql connect mediflow-db --user=mediflow_user --database=mediflow_production

# Your SQLAlchemy models will auto-create tables on first backend start
# Or run migrations if using Alembic
```

---

## 📊 Cost Estimation

### Free Tier (Good for development/testing)
- Cloud Run: 2 million requests/month free
- Cloud SQL: Not included in free tier
- Secret Manager: First 6 secrets free

### Estimated Monthly Costs (Low Traffic)
- Cloud Run Backend: $5-15/month
- Cloud Run Frontend: $3-8/month
- Cloud SQL (db-f1-micro): $7-10/month
- **Total: ~$15-35/month**

### For Production (Medium Traffic)
- Cloud Run Backend: $20-50/month
- Cloud Run Frontend: $10-20/month
- Cloud SQL (db-g1-small): $25-40/month
- **Total: ~$55-110/month**

---

## 🔐 Security Best Practices

### 1. Use Secret Manager
✅ **Never** hardcode secrets in code
✅ Store all sensitive data in Secret Manager
✅ Rotate secrets regularly

### 2. Enable IAM Permissions
```bash
# Create service accounts
gcloud iam service-accounts create mediflow-backend-sa
gcloud iam service-accounts create mediflow-frontend-sa

# Grant minimum permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:mediflow-backend-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"
```

### 3. Configure CORS Properly
Update `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.run.app"],  # Specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Enable HTTPS Only
Cloud Run automatically provides HTTPS. Ensure:
- `allow_credentials=True` in CORS
- Use `https://` URLs everywhere
- Set `secure=True` on cookies

---

## 🔍 Monitoring & Logging

### View Logs
```bash
# Backend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=mediflow-backend" --limit 50

# Frontend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=mediflow-frontend" --limit 50
```

### Set Up Alerts
1. Go to Cloud Console → Monitoring
2. Create alert policies for:
   - High error rates
   - High latency
   - High memory usage

### Enable Application Performance Monitoring
```bash
# Install Cloud Trace
pip install google-cloud-trace

# Add to requirements.txt
echo "google-cloud-trace" >> backend/requirements.txt
```

---

## 🚦 Testing Deployment

### 1. Test Backend
```bash
BACKEND_URL="https://mediflow-backend-XXXXX.run.app"

# Health check
curl $BACKEND_URL/health

# API docs
open $BACKEND_URL/docs
```

### 2. Test Frontend
```bash
FRONTEND_URL="https://mediflow-frontend-XXXXX.run.app"

# Open in browser
open $FRONTEND_URL

# Check status
curl $FRONTEND_URL/api/status
```

### 3. End-to-End Test
1. Register new user
2. Login
3. Submit symptoms
4. Check AI analysis
5. View history

---

## 🔄 Continuous Deployment (CI/CD)

### Option: Cloud Build Trigger

Create `cloudbuild.yaml`:
```yaml
steps:
# Backend
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/mediflow-backend', './backend']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/mediflow-backend']
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  entrypoint: gcloud
  args:
  - 'run'
  - 'deploy'
  - 'mediflow-backend'
  - '--image=gcr.io/$PROJECT_ID/mediflow-backend'
  - '--region=us-central1'

# Frontend
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/mediflow-frontend', './frontend']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/mediflow-frontend']
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  entrypoint: gcloud
  args:
  - 'run'
  - 'deploy'
  - 'mediflow-frontend'
  - '--image=gcr.io/$PROJECT_ID/mediflow-frontend'
  - '--region=us-central1'
```

Connect to GitHub and enable auto-deploy on push to main.

---

## 🌐 Custom Domain Setup

### 1. Verify Domain Ownership
```bash
gcloud domains verify example.com
```

### 2. Map Domain to Cloud Run
```bash
# Backend
gcloud run domain-mappings create \
    --service mediflow-backend \
    --domain api.mediflow.ai \
    --region us-central1

# Frontend
gcloud run domain-mappings create \
    --service mediflow-frontend \
    --domain mediflow.ai \
    --region us-central1
```

### 3. Update DNS Records
Add the provided DNS records to your domain registrar.

---

## 📋 Checklist: Pre-Deployment

- [ ] Google Cloud account created
- [ ] Project created and billing enabled
- [ ] gcloud CLI installed and authenticated
- [ ] Hugging Face API token obtained
- [ ] Dockerfile tested locally
- [ ] Environment variables configured
- [ ] Secrets created in Secret Manager

## 📋 Checklist: Post-Deployment

- [ ] Backend health check passes
- [ ] Frontend loads successfully
- [ ] Can register new user
- [ ] Can login and get JWT token
- [ ] AI symptom analysis works
- [ ] Database persistence works
- [ ] Logs are visible in Cloud Console
- [ ] HTTPS working
- [ ] Custom domain configured (optional)

---

## 🐛 Troubleshooting

### Backend won't deploy
```bash
# Check logs
gcloud run services logs read mediflow-backend --region us-central1

# Check build logs
gcloud builds log $(gcloud builds list --limit=1 --format='value(id)')
```

### Database connection issues
```bash
# Test Cloud SQL connection
gcloud sql connect mediflow-db --user=mediflow_user

# Check if instance is running
gcloud sql instances describe mediflow-db
```

### Frontend can't reach backend
```bash
# Verify CORS settings in backend
# Check API_BASE_URL in frontend env vars
gcloud run services describe mediflow-frontend --region us-central1 --format='value(spec.template.spec.containers[0].env)'
```

### High costs
```bash
# Check current spending
gcloud billing accounts list
gcloud billing projects describe $PROJECT_ID

# Reduce min-instances to 0 for dev
gcloud run services update mediflow-backend --min-instances 0
```

---

## 📚 Additional Resources

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Flask on Cloud Run](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service)

---

## 🎉 Success!

Your MediFlow AI application is now running on Google Cloud!

- **Backend**: Serverless, auto-scaling, production-ready
- **Frontend**: Fast, responsive, globally distributed
- **Database**: Managed, backed up, highly available

**Next Steps:**
1. Monitor logs and performance
2. Set up alerts
3. Configure custom domain
4. Enable CI/CD
5. Scale as needed

---

**Need Help?**
- Cloud Console: https://console.cloud.google.com
- Support: https://cloud.google.com/support

**Deployment Guide Version**: 1.0.0
**Last Updated**: 2024
