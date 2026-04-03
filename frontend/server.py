"""
MediFlow AI — Flask Frontend Application
Serves Jinja2 templates and connects to FastAPI backend via HTTP.
"""

import os
from datetime import datetime
import requests
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "mediflow-flask-secret-2024")

# ─── Backend API URL ──────────────────────────────────────
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


# ─── Helper: Call backend API ─────────────────────────────
def api_call(method: str, endpoint: str, json=None, token=None, timeout=10):
    """Make an authenticated HTTP call to the FastAPI backend."""
    url = f"{API_BASE}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        resp = getattr(requests, method)(url, json=json, headers=headers, timeout=timeout)
        return resp.json(), resp.status_code
    except requests.exceptions.ConnectionError:
        return {"detail": "Backend server is offline."}, 503
    except Exception as e:
        return {"detail": str(e)}, 500


# ─── Auth Guard ───────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "token" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get("role") not in roles:
                flash("Access denied.", "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return decorated
    return decorator


# ════════════════════════════════════════════════════════════
# PUBLIC ROUTES
# ════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Landing page — public."""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "token" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        data, status = api_call("post", "/auth/login", json={
            "email": email,
            "password": password,
        })

        if status == 200:
            session["token"] = data["access_token"]
            session["role"] = data["role"]
            session["user_id"] = data["user_id"]
            session["email"] = email
            flash(f"Welcome back! Logged in as {data['role'].capitalize()}.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash(data.get("detail", "Invalid credentials."), "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "token" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "patient")

        data, status = api_call("post", "/auth/register", json={
            "email": email,
            "password": password,
            "role": role,
        })

        if status == 201:
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash(data.get("detail", "Registration failed."), "danger")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ════════════════════════════════════════════════════════════
# PROTECTED ROUTES
# ════════════════════════════════════════════════════════════

@app.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard — fetches live stats from backend."""
    token = session["token"]
    role = session["role"]
    stats = {}

    # Admins & doctors see analytics
    if role in ("admin", "doctor"):
        analytics, _ = api_call("get", "/admin/analytics", token=token)
        stats = analytics if isinstance(analytics, dict) else {}

    # Patient sees own profile
    if role == "patient":
        profile, _ = api_call("get", "/patient/profile", token=token)
        stats["patient"] = profile if isinstance(profile, dict) else {}

    return render_template("dashboard.html",
                           stats=stats,
                           role=role,
                           email=session.get("email", ""),
                           now_hour=datetime.now().hour)


@app.route("/patients")
@login_required
@role_required("doctor", "admin")
def patients():
    """Patient panel — list all patients with priorities."""
    token = session["token"]
    priority_filter = request.args.get("priority")

    endpoint = "/doctor/patients"
    if priority_filter:
        endpoint += f"?priority={priority_filter}"

    data, status = api_call("get", endpoint, token=token)
    patient_list = data if isinstance(data, list) else []

    return render_template("patients.html",
                           patients=patient_list,
                           selected_priority=priority_filter,
                           role=session["role"])


@app.route("/appointments")
@login_required
def appointments():
    """Appointments page — shows schedule based on role."""
    token = session["token"]
    role = session["role"]

    if role == "patient":
        data, _ = api_call("get", "/patient/appointments", token=token)
    else:
        data, _ = api_call("get", "/doctor/schedule", token=token)

    appt_list = data if isinstance(data, list) else []
    return render_template("appointments.html",
                           appointments=appt_list,
                           role=role)


@app.route("/symptoms", methods=["GET", "POST"])
@login_required
@role_required("patient")
def symptoms():
    """Patient submits symptoms → AI triage result."""
    result = None

    if request.method == "POST":
        symptoms_text = request.form.get("symptoms", "").strip()
        if symptoms_text:
            data, status = api_call(
                "post", "/patient/symptoms",
                json={"symptoms": symptoms_text},
                token=session["token"]
            )
            if status == 200:
                result = data
            else:
                flash(data.get("detail", "Analysis failed."), "danger")
        else:
            flash("Please describe your symptoms.", "warning")

    return render_template("symptoms.html", result=result)


@app.route("/history")
@login_required
@role_required("patient")
def history():
    """Patient symptom history."""
    data, _ = api_call("get", "/patient/history", token=session["token"])
    logs = data if isinstance(data, list) else []
    return render_template("history.html", logs=logs)


@app.route("/ai-chat")
@login_required
def ai_chat():
    """AI Chatbot page."""
    return render_template("ai_chat.html", role=session.get("role"))


# ════════════════════════════════════════════════════════════
# API PROXY ENDPOINTS (called by frontend JS)
# ════════════════════════════════════════════════════════════

@app.route("/api/chat", methods=["POST"])
@login_required
def proxy_chat():
    """Proxy /ai/chat to backend — called from chat UI via fetch()."""
    body = request.get_json()
    data, status = api_call("post", "/ai/chat",
                            json={"message": body.get("message", "")},
                            token=session["token"])
    return jsonify(data), status


@app.route("/api/analyze", methods=["POST"])
@login_required
def proxy_analyze():
    """Proxy /ai/analyze to backend."""
    body = request.get_json()
    data, status = api_call("post", "/ai/analyze",
                            json={"symptoms": body.get("symptoms", "")},
                            token=session["token"])
    return jsonify(data), status


@app.route("/api/status")
def api_status():
    """Check backend connectivity."""
    data, status = api_call("get", "/health")
    return jsonify({"flask": "online", "backend": data, "status": status})


# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Use PORT env var for Cloud Run compatibility (defaults to 8080)
    port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 5000)))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    print(f"\n🔷 MediFlow AI Flask Frontend → http://localhost:{port}")
    print(f"🔷 Backend API target         → {API_BASE}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
