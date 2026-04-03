#!/bin/bash
# ─────────────────────────────────────────────────────────────
# MediFlow AI — Google Cloud Deployment Script (Backend)
# ─────────────────────────────────────────────────────────────

set -e

# ── Configuration (UPDATE THESE) ──────────────────────────────
PROJECT_ID="your-gcp-project-id"
REGION="us-central1"  # or asia-south1, europe-west1, etc.
SERVICE_NAME="mediflow-backend"
IMAGE_NAME="mediflow-backend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  MediFlow AI - Backend Deployment to Google Cloud Run${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}\n"

# ── Step 1: Set GCP Project ───────────────────────────────────
echo -e "${YELLOW}[1/7] Setting GCP Project...${NC}"
gcloud config set project $PROJECT_ID
echo -e "${GREEN}✓ Project set to: $PROJECT_ID${NC}\n"

# ── Step 2: Enable Required APIs ──────────────────────────────
echo -e "${YELLOW}[2/7] Enabling required Google Cloud APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com
echo -e "${GREEN}✓ APIs enabled${NC}\n"

# ── Step 3: Build Docker Image ────────────────────────────────
echo -e "${YELLOW}[3/7] Building Docker image...${NC}"
cd backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/$IMAGE_NAME:latest
cd ..
echo -e "${GREEN}✓ Docker image built and pushed${NC}\n"

# ── Step 4: Create Secrets (if not exists) ────────────────────
echo -e "${YELLOW}[4/7] Checking secrets...${NC}"

# Check if secret exists, create if not
if ! gcloud secrets describe mediflow-secrets &>/dev/null; then
    echo "Creating secrets..."
    
    # Generate a secure random key for JWT
    JWT_SECRET=$(openssl rand -base64 32)
    
    # Create secret with JWT key
    echo -n "$JWT_SECRET" | gcloud secrets create mediflow-secrets \
        --data-file=- \
        --replication-policy="automatic"
    
    # Add Hugging Face token (you'll need to add this manually)
    echo -e "${YELLOW}Please add your Hugging Face API token to Secret Manager:${NC}"
    echo "gcloud secrets versions add mediflow-secrets --data-file=<path-to-hf-token>"
else
    echo -e "${GREEN}✓ Secrets already exist${NC}"
fi
echo ""

# ── Step 5: Deploy to Cloud Run ───────────────────────────────
echo -e "${YELLOW}[5/7] Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$IMAGE_NAME:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 1 \
    --max-instances 10 \
    --timeout 300 \
    --set-env-vars "APP_ENV=production,USE_HF_API=true,ALGORITHM=HS256" \
    --set-secrets "SECRET_KEY=mediflow-secrets:latest,HUGGINGFACE_API_TOKEN=mediflow-secrets:latest"

echo -e "${GREEN}✓ Backend deployed to Cloud Run${NC}\n"

# ── Step 6: Get Service URL ───────────────────────────────────
echo -e "${YELLOW}[6/7] Retrieving service URL...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo -e "${GREEN}✓ Backend URL: $SERVICE_URL${NC}\n"

# ── Step 7: Test Deployment ───────────────────────────────────
echo -e "${YELLOW}[7/7] Testing deployment...${NC}"
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $SERVICE_URL/health)
if [ $HEALTH_STATUS -eq 200 ]; then
    echo -e "${GREEN}✓ Health check passed!${NC}\n"
else
    echo -e "${RED}✗ Health check failed (HTTP $HEALTH_STATUS)${NC}\n"
fi

# ── Summary ───────────────────────────────────────────────────
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Backend Deployment Complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "Service URL:    ${GREEN}$SERVICE_URL${NC}"
echo -e "API Docs:       ${GREEN}$SERVICE_URL/docs${NC}"
echo -e "Health Check:   ${GREEN}$SERVICE_URL/health${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Set up Cloud SQL database (see DEPLOYMENT.md)"
echo "2. Update DATABASE_URL environment variable"
echo "3. Deploy frontend with backend URL: $SERVICE_URL"
echo ""
