# Therapist 🩺 — Offline-First Physiotherapy Coach

Therapist is a highly resilient, offline-first web application designed to assist with post-op knee rehabilitation. It serves as a hands-free guide, walking users through physical therapy exercises using precise audio-visual cues, automated timers, and repetition tracking.

## 🚀 Core Features
- **Hands-Free Timers & Rep Counters**: Automated pacing without touching the screen.
- **Bilingual Audio**: Full text-to-speech coaching in English and Malayalam.
- **Offline-First Resilience**: Syncs data automatically when connection is restored.
- **Screen WakeLock**: Prevents screen timeouts during exercises.
- **Progress Tracking**: Daily adherence graphs and session history.

## 🛠️ Quick Setup
```bash
git clone <repository-url>
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

[📖 Read the full story, detailed technical architecture, and deployment guide ➔](read_more.md)
