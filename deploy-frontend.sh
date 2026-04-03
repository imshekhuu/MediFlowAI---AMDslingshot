#!/bin/bash
# ─────────────────────────────────────────────────────────────
# MediFlow AI — Google Cloud Deployment Script (Frontend)
# ─────────────────────────────────────────────────────────────

set -e

# ── Configuration (UPDATE THESE) ──────────────────────────────
PROJECT_ID="your-gcp-project-id"
REGION="us-central1"
SERVICE_NAME="mediflow-frontend"
IMAGE_NAME="mediflow-frontend"
BACKEND_URL="https://mediflow-backend-XXXXX.run.app"  # Update with your backend URL

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  MediFlow AI - Frontend Deployment to Google Cloud Run${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}\n"

# ── Step 1: Set GCP Project ───────────────────────────────────
echo -e "${YELLOW}[1/5] Setting GCP Project...${NC}"
gcloud config set project $PROJECT_ID
echo -e "${GREEN}✓ Project set to: $PROJECT_ID${NC}\n"

# ── Step 2: Build Docker Image ────────────────────────────────
echo -e "${YELLOW}[2/5] Building Docker image...${NC}"
cd frontend
gcloud builds submit --tag gcr.io/$PROJECT_ID/$IMAGE_NAME:latest
cd ..
echo -e "${GREEN}✓ Docker image built and pushed${NC}\n"

# ── Step 3: Create Flask Secret (if not exists) ───────────────
echo -e "${YELLOW}[3/5] Checking Flask secret...${NC}"
if ! gcloud secrets describe flask-secret-key &>/dev/null; then
    echo "Creating Flask secret..."
    FLASK_SECRET=$(openssl rand -base64 32)
    echo -n "$FLASK_SECRET" | gcloud secrets create flask-secret-key \
        --data-file=- \
        --replication-policy="automatic"
    echo -e "${GREEN}✓ Flask secret created${NC}"
else
    echo -e "${GREEN}✓ Flask secret already exists${NC}"
fi
echo ""

# ── Step 4: Deploy to Cloud Run ───────────────────────────────
echo -e "${YELLOW}[4/5] Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$IMAGE_NAME:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 1 \
    --max-instances 5 \
    --timeout 300 \
    --set-env-vars "API_BASE_URL=$BACKEND_URL,FLASK_DEBUG=false" \
    --set-secrets "FLASK_SECRET_KEY=flask-secret-key:latest"

echo -e "${GREEN}✓ Frontend deployed to Cloud Run${NC}\n"

# ── Step 5: Get Service URL and Test ──────────────────────────
echo -e "${YELLOW}[5/5] Retrieving service URL and testing...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo -e "${GREEN}✓ Frontend URL: $SERVICE_URL${NC}\n"

HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $SERVICE_URL/)
if [ $HEALTH_STATUS -eq 200 ]; then
    echo -e "${GREEN}✓ Health check passed!${NC}\n"
else
    echo -e "${RED}✗ Health check failed (HTTP $HEALTH_STATUS)${NC}\n"
fi

# ── Summary ───────────────────────────────────────────────────
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Frontend Deployment Complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "Frontend URL:   ${GREEN}$SERVICE_URL${NC}"
echo -e "Backend URL:    ${GREEN}$BACKEND_URL${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Open: $SERVICE_URL"
echo "2. Register a new account and test"
echo "3. (Optional) Set up custom domain"
echo ""
