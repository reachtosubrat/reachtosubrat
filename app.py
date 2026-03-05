import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# ── Security config ──────────────────────────────────────────────────────────
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=2)

# ── Rate limiter (prevents brute-force) ─────────────────────────────────────
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# ── Data file ────────────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "site_data.json")
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

DEFAULT_DATA = {
    "hero": {
        "name": "Subrat",
        "tagline": "Cybersecurity | Tech | 0xSubrat",
        "bio": "Cybersecurity researcher & tech content creator. I break things down — literally and digitally."
    },
    "social_links": [
        {"platform": "YouTube",   "icon": "youtube",   "url": "", "handle": "@0xSubrat",        "active": False},
        {"platform": "Instagram", "icon": "instagram", "url": "", "handle": "@reachtosubrat",   "active": False},
        {"platform": "LinkedIn",  "icon": "linkedin",  "url": "", "handle": "reachtosubrat",    "active": False},
        {"platform": "GitHub",    "icon": "github",    "url": "", "handle": "reachtosubrat",    "active": False},
        {"platform": "Twitter/X", "icon": "twitter",   "url": "", "handle": "@reachtosubrat",   "active": False}
    ],
    "email": "reachtosubrat@gmail.com",
    "show_email": True
}

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Admin credentials (env vars — never hardcoded in prod) ──────────────────
ADMIN_USER = os.environ.get("ADMIN_USER", "reachtosubrat")
# Store hashed password only
_raw_pass  = os.environ.get("ADMIN_PASS", "ChangeThisPassword123!")
ADMIN_HASH = hashlib.sha256(_raw_pass.encode()).hexdigest()

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

# ── Public routes ────────────────────────────────────────────────────────────
@app.route("/")
def index():
    data = load_data()
    return render_template("index.html", data=data)

# ── Admin routes ─────────────────────────────────────────────────────────────
@app.route("/admin", methods=["GET"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html")

@app.route("/admin/auth", methods=["POST"])
@limiter.limit("5 per minute")          # brute-force protection
def admin_auth():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if username == ADMIN_USER and hash_password(password) == ADMIN_HASH:
        session.permanent = True
        session["admin_logged_in"] = True
        session["login_time"] = datetime.utcnow().isoformat()
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html", error="Invalid credentials. Try again.")

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    data = load_data()
    return render_template("admin_dashboard.html", data=data)

@app.route("/admin/update", methods=["POST"])
@login_required
def admin_update():
    data = load_data()
    payload = request.get_json(silent=True) or {}
    section = payload.get("section")

    if section == "hero":
        data["hero"]["name"]    = payload.get("name",    data["hero"]["name"])[:80]
        data["hero"]["tagline"] = payload.get("tagline", data["hero"]["tagline"])[:120]
        data["hero"]["bio"]     = payload.get("bio",     data["hero"]["bio"])[:400]

    elif section == "social":
        links = payload.get("links", [])
        # Validate & sanitise
        clean = []
        for lnk in links[:10]:
            clean.append({
                "platform": str(lnk.get("platform",""))[:30],
                "icon":     str(lnk.get("icon",""))[:20],
                "url":      str(lnk.get("url",""))[:300],
                "handle":   str(lnk.get("handle",""))[:60],
                "active":   bool(lnk.get("active", False))
            })
        data["social_links"] = clean

    elif section == "email":
        data["email"]      = str(payload.get("email", data["email"]))[:100]
        data["show_email"] = bool(payload.get("show_email", True))

    else:
        return jsonify({"ok": False, "msg": "Unknown section"}), 400

    save_data(data)
    return jsonify({"ok": True})

@app.route("/admin/logout")
@login_required
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

# ── Security headers ─────────────────────────────────────────────────────────
@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"]  = "nosniff"
    response.headers["X-Frame-Options"]         = "DENY"
    response.headers["X-XSS-Protection"]        = "1; mode=block"
    response.headers["Referrer-Policy"]         = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "script-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:;"
    )
    return response

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
