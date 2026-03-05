# reachtosubrat.com — Setup Guide

## 🗂 Project Structure
```
reachtosubrat/
├── app.py                      # Flask backend
├── requirements.txt            # Python dependencies
├── netlify.toml                # Netlify config
├── templates/
│   ├── index.html              # Main website
│   ├── admin_login.html        # Admin login page
│   └── admin_dashboard.html    # Admin panel
├── netlify/functions/
│   └── app.py                  # Serverless wrapper
└── data/
    └── site_data.json          # Your site content (auto-created)
```

---

## 🚀 Deploy on Netlify (Step by Step)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/reachtosubrat
git push -u origin main
```

### Step 2 — Connect to Netlify
1. Go to https://netlify.com → Log in
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect your GitHub → Select the repo
4. Build settings are auto-detected from `netlify.toml`
5. Click **Deploy**

### Step 3 — Set Environment Variables (IMPORTANT 🔐)
In Netlify → Site Settings → Environment Variables, add:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | (generate one: `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `ADMIN_USER` | `reachtosubrat` |
| `ADMIN_PASS` | **Your NEW secure password** (don't use the one from chat!) |

### Step 4 — Connect Custom Domain
1. Netlify → Domain Settings → Add custom domain
2. Add `reachtosubrat.com`
3. Update your domain's DNS to point to Netlify

---

## 🔐 Admin Panel

- URL: `https://reachtosubrat.com/admin`
- Login with your `ADMIN_USER` and `ADMIN_PASS` env vars
- From the dashboard you can:
  - Edit your name, tagline, bio
  - Add/toggle social links (YouTube, Instagram, LinkedIn, GitHub, Twitter)
  - Update contact email

---

## ⚠️ Security Notes

1. **CHANGE YOUR PASSWORD** — The password shared in chat is compromised. Set a new one in Netlify env vars.
2. **Never commit `.env` files** to GitHub
3. Rate limiting is active — 5 login attempts per minute max
4. All security headers are set (XSS, CSRF, Clickjacking protection)
5. Passwords are SHA-256 hashed — never stored in plaintext
6. Sessions expire after 2 hours automatically

---

## 💻 Run Locally

```bash
pip install -r requirements.txt

# Set env vars
export SECRET_KEY="your-secret-key"
export ADMIN_USER="reachtosubrat"
export ADMIN_PASS="your-password"

python app.py
# Visit http://localhost:5000
```

---

## 📱 Responsive
Works on Android, iOS, Windows, Mac, Linux — all screen sizes.
