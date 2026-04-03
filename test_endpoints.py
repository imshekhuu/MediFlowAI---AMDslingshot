"""
MediFlow AI - Endpoint Testing Script
Tests all backend API endpoints to ensure connectivity and functionality
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:5000"

# Colors for console output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

# Test Data
test_user = {
    "email": f"test_{datetime.now().timestamp()}@mediflow.ai",
    "password": "TestPass123!",
    "role": "patient"
}

test_doctor = {
    "email": f"doctor_{datetime.now().timestamp()}@mediflow.ai",
    "password": "DoctorPass123!",
    "role": "doctor"
}

test_admin = {
    "email": f"admin_{datetime.now().timestamp()}@mediflow.ai",
    "password": "AdminPass123!",
    "role": "admin"
}

def test_health_endpoints():
    """Test health check endpoints"""
    print("\n" + "="*60)
    print("Testing Health Endpoints")
    print("="*60)
    
    try:
        # Test root endpoint
        resp = requests.get(f"{API_BASE}/")
        if resp.status_code == 200:
            print_success(f"GET / - {resp.json()['status']}")
        else:
            print_error(f"GET / - Status {resp.status_code}")
        
        # Test health endpoint
        resp = requests.get(f"{API_BASE}/health")
        if resp.status_code == 200:
            print_success(f"GET /health - {resp.json()['status']}")
        else:
            print_error(f"GET /health - Status {resp.status_code}")
            
    except requests.exceptions.ConnectionError:
        print_error("Backend server is offline!")
        return False
    
    return True

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("\n" + "="*60)
    print("Testing Authentication Endpoints")
    print("="*60)
    
    # Test registration
    try:
        resp = requests.post(f"{API_BASE}/auth/register", json=test_user)
        if resp.status_code == 201:
            print_success(f"POST /auth/register - User created")
        else:
            print_error(f"POST /auth/register - {resp.json().get('detail', 'Failed')}")
            return None
    except Exception as e:
        print_error(f"POST /auth/register - {str(e)}")
        return None
    
    # Test login
    try:
        resp = requests.post(f"{API_BASE}/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        if resp.status_code == 200:
            token_data = resp.json()
            print_success(f"POST /auth/login - Token received")
            return token_data["access_token"]
        else:
            print_error(f"POST /auth/login - {resp.json().get('detail', 'Failed')}")
            return None
    except Exception as e:
        print_error(f"POST /auth/login - {str(e)}")
        return None

def test_patient_endpoints(token):
    """Test patient endpoints"""
    print("\n" + "="*60)
    print("Testing Patient Endpoints")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Register patient profile
    patient_data = {
        "name": "Test Patient",
        "age": 30,
        "gender": "Male",
        "blood_group": "O+",
        "phone": "+1234567890",
        "medical_history": "No significant history"
    }
    
    try:
        resp = requests.post(f"{API_BASE}/patient/register", json=patient_data, headers=headers)
        if resp.status_code == 201:
            print_success("POST /patient/register - Profile created")
            patient_id = resp.json()["id"]
        else:
            print_error(f"POST /patient/register - {resp.json().get('detail', 'Failed')}")
            patient_id = None
    except Exception as e:
        print_error(f"POST /patient/register - {str(e)}")
        patient_id = None
    
    # Get patient profile
    try:
        resp = requests.get(f"{API_BASE}/patient/profile", headers=headers)
        if resp.status_code == 200:
            print_success("GET /patient/profile - Profile retrieved")
        else:
            print_error(f"GET /patient/profile - Status {resp.status_code}")
    except Exception as e:
        print_error(f"GET /patient/profile - {str(e)}")
    
    # Submit symptoms
    symptoms_data = {"symptoms": "I have a mild headache and slight fever"}
    try:
        resp = requests.post(f"{API_BASE}/patient/symptoms", json=symptoms_data, headers=headers)
        if resp.status_code == 200:
            result = resp.json()
            print_success(f"POST /patient/symptoms - Priority: {result['priority']}")
        else:
            print_error(f"POST /patient/symptoms - Status {resp.status_code}")
    except Exception as e:
        print_error(f"POST /patient/symptoms - {str(e)}")
    
    # Get symptom history
    try:
        resp = requests.get(f"{API_BASE}/patient/history", headers=headers)
        if resp.status_code == 200:
            print_success(f"GET /patient/history - {len(resp.json())} entries")
        else:
            print_error(f"GET /patient/history - Status {resp.status_code}")
    except Exception as e:
        print_error(f"GET /patient/history - {str(e)}")
    
    # Get appointments
    try:
        resp = requests.get(f"{API_BASE}/patient/appointments", headers=headers)
        if resp.status_code == 200:
            print_success(f"GET /patient/appointments - {len(resp.json())} appointments")
        else:
            print_error(f"GET /patient/appointments - Status {resp.status_code}")
    except Exception as e:
        print_error(f"GET /patient/appointments - {str(e)}")
    
    return patient_id

def test_ai_endpoints(token):
    """Test AI endpoints"""
    print("\n" + "="*60)
    print("Testing AI Endpoints")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test AI analysis
    try:
        resp = requests.post(f"{API_BASE}/ai/analyze", 
                           json={"symptoms": "chest pain and difficulty breathing"},
                           headers=headers)
        if resp.status_code == 200:
            result = resp.json()
            print_success(f"POST /ai/analyze - Priority: {result['priority']}")
        else:
            print_error(f"POST /ai/analyze - Status {resp.status_code}")
    except Exception as e:
        print_error(f"POST /ai/analyze - {str(e)}")
    
    # Test AI chat
    try:
        resp = requests.post(f"{API_BASE}/ai/chat",
                           json={"message": "What should I do for a headache?"},
                           headers=headers)
        if resp.status_code == 200:
            print_success("POST /ai/chat - Response received")
        else:
            print_error(f"POST /ai/chat - Status {resp.status_code}")
    except Exception as e:
        print_error(f"POST /ai/chat - {str(e)}")
    
    # Test AI status
    try:
        resp = requests.get(f"{API_BASE}/ai/status", headers=headers)
        if resp.status_code == 200:
            result = resp.json()
            print_success(f"GET /ai/status - Engine: {result.get('llm_engine', 'Unknown')}")
        else:
            print_error(f"GET /ai/status - Status {resp.status_code}")
    except Exception as e:
        print_error(f"GET /ai/status - {str(e)}")

def test_doctor_endpoints():
    """Test doctor endpoints with a doctor account"""
    print("\n" + "="*60)
    print("Testing Doctor Endpoints")
    print("="*60)
    
    # Register doctor
    try:
        resp = requests.post(f"{API_BASE}/auth/register", json=test_doctor)
        if resp.status_code in [201, 409]:  # 409 if already exists
            print_success("Doctor account ready")
        else:
            print_error(f"Doctor registration failed: {resp.json().get('detail')}")
            return
    except Exception as e:
        print_error(f"Doctor registration error: {str(e)}")
        return
    
    # Login as doctor
    try:
        resp = requests.post(f"{API_BASE}/auth/login", json={
            "email": test_doctor["email"],
            "password": test_doctor["password"]
        })
        if resp.status_code == 200:
            token = resp.json()["access_token"]
            print_success("Doctor login successful")
        else:
            print_error(f"Doctor login failed")
            return
    except Exception as e:
        print_error(f"Doctor login error: {str(e)}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get patients
    try:
        resp = requests.get(f"{API_BASE}/doctor/patients", headers=headers)
        if resp.status_code == 200:
            print_success(f"GET /doctor/patients - {len(resp.json())} patients")
        else:
            print_error(f"GET /doctor/patients - Status {resp.status_code}")
    except Exception as e:
        print_error(f"GET /doctor/patients - {str(e)}")
    
    # Get schedule
    try:
        resp = requests.get(f"{API_BASE}/doctor/schedule", headers=headers)
        if resp.status_code == 200:
            print_success(f"GET /doctor/schedule - {len(resp.json())} appointments")
        else:
            print_error(f"GET /doctor/schedule - Status {resp.status_code}")
    except Exception as e:
        print_error(f"GET /doctor/schedule - {str(e)}")
    
    # Suggest appointment slot
    try:
        resp = requests.get(f"{API_BASE}/doctor/suggest-slot?priority=Emergency", headers=headers)
        if resp.status_code == 200:
            print_success("GET /doctor/suggest-slot - Slot suggested")
        else:
            print_error(f"GET /doctor/suggest-slot - Status {resp.status_code}")
    except Exception as e:
        print_error(f"GET /doctor/suggest-slot - {str(e)}")

def test_admin_endpoints():
    """Test admin endpoints"""
    print("\n" + "="*60)
    print("Testing Admin Endpoints")
    print("="*60)
    
    # Register admin
    try:
        resp = requests.post(f"{API_BASE}/auth/register", json=test_admin)
        if resp.status_code in [201, 409]:
            print_success("Admin account ready")
        else:
            print_error(f"Admin registration failed")
            return
    except Exception as e:
        print_error(f"Admin registration error: {str(e)}")
        return
    
    # Login as admin
    try:
        resp = requests.post(f"{API_BASE}/auth/login", json={
            "email": test_admin["email"],
            "password": test_admin["password"]
        })
        if resp.status_code == 200:
            token = resp.json()["access_token"]
            print_success("Admin login successful")
        else:
            print_error("Admin login failed")
            return
    except Exception as e:
        print_error(f"Admin login error: {str(e)}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get analytics
    try:
        resp = requests.get(f"{API_BASE}/admin/analytics", headers=headers)
        if resp.status_code == 200:
            result = resp.json()
            print_success(f"GET /admin/analytics - {result['summary']['total_users']} users")
        else:
            print_error(f"GET /admin/analytics - Status {resp.status_code}")
    except Exception as e:
        print_error(f"GET /admin/analytics - {str(e)}")

def test_frontend_connectivity():
    """Test frontend server connectivity"""
    print("\n" + "="*60)
    print("Testing Frontend Connectivity")
    print("="*60)
    
    try:
        resp = requests.get(FRONTEND_BASE, timeout=5)
        if resp.status_code == 200:
            print_success("Frontend server is online")
        else:
            print_warning(f"Frontend returned status {resp.status_code}")
    except requests.exceptions.ConnectionError:
        print_warning("Frontend server is offline")
    except Exception as e:
        print_error(f"Frontend test error: {str(e)}")

def main():
    """Main test runner"""
    print("\n" + "="*60)
    print("🏥 MediFlow AI - Endpoint Test Suite")
    print("="*60)
    print_info(f"Backend API: {API_BASE}")
    print_info(f"Frontend: {FRONTEND_BASE}")
    
    # Test health endpoints first
    if not test_health_endpoints():
        print_error("\nBackend server is not running!")
        print_info("Please start the backend server first:")
        print_info("  cd backend && python -m uvicorn app.main:app --reload")
        return
    
    # Test authentication
    token = test_auth_endpoints()
    if not token:
        print_error("\nAuthentication tests failed!")
        return
    
    # Test patient endpoints
    patient_id = test_patient_endpoints(token)
    
    # Test AI endpoints
    test_ai_endpoints(token)
    
    # Test doctor endpoints
    test_doctor_endpoints()
    
    # Test admin endpoints
    test_admin_endpoints()
    
    # Test frontend
    test_frontend_connectivity()
    
    print("\n" + "="*60)
    print("✨ Test Suite Complete!")
    print("="*60)

if __name__ == "__main__":
    main()
