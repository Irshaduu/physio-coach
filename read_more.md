# 📖 Therapist — Detailed Documentation

## 💡 The Story (Why I Built This)
This project was born out of personal necessity. Following an arthroscopic knee surgery, I found post-op physiotherapy incredibly challenging. For an ADHD brain, mentally counting 10-second holds while keeping track of 20 repetitions—through the pain—caused massive task initiation hesitation and mental exhaustion.

Instead of struggling, I built this system to act as a strict, hands-free personal coach. It forces adherence, removes the cognitive load of counting, and ensures medical routines are completed accurately even when motivation is low.

## ✨ Technical Highlights & Architecture
- **3-Tier Audio Fallback System:** To ensure zero latency and zero recurring API costs, the app uses a cascading audio system: Web Speech API (Native) ➔ Cached `gTTS` MP3 Manifest (Bilingual) ➔ Live Server API.
- **Screen WakeLock API:** Integrated the browser WakeLock API to prevent the patient's screen from timing out and going black in the middle of a painful stretch or exercise.
- **Offline-First State Machine:** Uses `localStorage` to queue session data if the clinic or home network drops, syncing silently with the server once the connection is restored.
- **Optimized Backend:** Built with Django, utilizing `select_related` and `prefetch_related` to eliminate N+1 query bottlenecks and ensure a blazing-fast, responsive dashboard.

## 📱 Detailed Features
- **Hands-Free Timers & Rep Counters:** Start the workout and let the app handle the counting and timing.
- **Bilingual Audio:** Full text-to-speech coaching available in both **English** and **Malayalam**.
- **Progress Tracking:** Visual dashboard with daily adherence graphs, completion scores, and session history.
- **Mobile-First UI:** Clean, distraction-free dark mode interface optimized specifically for mobile browsers.

## 📸 Screenshots
*(Recommended: Upload your dark-theme UI screenshots to a /docs folder and link them here)*
![Player UI](docs/player-ui.jpg)
![Dashboard](docs/dashboard.jpg)

## 🛠️ Full Tech Stack
- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, Vanilla JavaScript (Zero-bloat architecture)
- **Database**: SQLite (Configured for single-tenant/personal use)
- **Audio Integration**: Python `gTTS` (Google Text-to-Speech)

## ⚙️ Deployment & Production

### PythonAnywhere Setup:
1. Clone the repository to your PythonAnywhere environment.
2. Create a virtual environment and install `requirements.txt`.
3. Set up the Web App in PythonAnywhere, configuring it to point to `rehabloop.wsgi`.
4. Add the following Static and Media paths in the Web tab:
   - `/static/` -> `PROJECT_PATH/static/`
   - `/media/` -> `PROJECT_PATH/media/`
