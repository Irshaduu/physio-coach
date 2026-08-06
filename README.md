# Therapist 🩺 — Physiotherapy Coach

> **A hands-free physiotherapy web app** built after knee surgery to eliminate the cognitive load of manual counting during painful rehabilitation exercises.

**Live Demo →** [therapist.pythonanywhere.com](https://therapist.pythonanywhere.com)

---

## 💡 The Problem

Following arthroscopic knee surgery, post-op physiotherapy requires completing dozens of reps of timed holds — often while in significant pain. Mentally counting 10-second holds, tracking 20 repetitions, and managing 9 exercises creates serious cognitive overhead, especially for someone with ADHD. This app eliminates that overhead entirely.

---

## 🚀 Core Features

| Feature | Description |
|---------|-------------|
| **Hands-Free Timers & Rep Counters** | Start the workout, set the device down. The app handles all counting and timing automatically. |
| **3-Tier Audio Fallback** | Web Speech API (zero latency) → Pre-cached gTTS MP3s (offline) → Live Google TTS API |
| **Bilingual Coaching** | Full text-to-speech coaching in **English** and **Malayalam** |
| **Offline-First** | Workouts log to `localStorage` when offline and silently sync to the server when reconnected |
| **Screen WakeLock** | Prevents the screen from going dark mid-exercise using the browser WakeLock API |
| **Progress Dashboard** | Daily adherence graphs, completion scores, and full session history |

---

## 🛠️ Tech Stack

- **Backend:** Django (Python) — with `select_related`/`prefetch_related` to eliminate N+1 queries
- **Frontend:** Vanilla JavaScript, HTML, CSS — zero framework bloat for instant mobile loads
- **Database:** SQLite (single-tenant, personal-use design)
- **Audio:** Python `gTTS` (Google Text-to-Speech) for bilingual MP3 generation
- **Hosting:** PythonAnywhere (free tier)

---

## ⚙️ Local Setup

### 1. Clone & create environment

```bash
git clone https://github.com/Irshaduu/rehab-coach.git
cd rehab-coach
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
# Copy the template and fill in your values
copy .env.example .env
```

Open `.env` and set your `SECRET_KEY`. Generate a fresh one with:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Run the app

```bash
python manage.py migrate
python manage.py createsuperuser    # Create your admin account
python manage.py runserver
```

Then visit **http://127.0.0.1:8000** and log in with the superuser you just created.

> **Note:** On first run, the audio cache (`media/tts_cache/`) is empty. The app will auto-generate MP3 files on demand via the Google TTS API — an internet connection is required for initial audio generation only.

---

## 🌐 PythonAnywhere Deployment

1. Clone the repo to your PythonAnywhere environment.
2. Create a virtual environment and install `requirements.txt`.
3. Set environment variables in the **WSGI configuration file**:
   ```python
   # In your WSGI file, before importing Django:
   import os
   os.environ['SECRET_KEY'] = 'your-production-secret-key'
   os.environ['DEBUG'] = 'False'
   os.environ['ALLOWED_HOSTS'] = 'yourusername.pythonanywhere.com'
   ```
4. In the **Web** tab, configure static and media paths:
   - `/static/` → `PROJECT_PATH/staticfiles/`
   - `/media/`  → `PROJECT_PATH/media/`
5. Run `python manage.py collectstatic` and reload the web app.

---

## 📖 Architecture & Design Decisions

→ [Read the full technical deep-dive](read_more.md)
