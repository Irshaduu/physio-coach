# 🤖 Project Rules & AI Context (Therapist 🩺)

> **Context for AI Agents**: Read this document to understand the core philosophy, structure, and needs of this project before making modifications.

## 🧠 Philosophy & Psychology
1. **The User is in Pain**: The end-user of this app is a post-op knee surgery patient. They are likely in pain, unmotivated, and struggling with "ADHD paralysis" or task hesitation. 
2. **Zero Cognitive Load**: The app must handle *everything*. Counting reps, timing holds, and transitioning between exercises must be fully automated. The user should only have to click "Start" and listen.
3. **Strict but Supportive**: The app acts as a strict personal coach. It forces adherence to medical routines while providing clear, authoritative audio cues.

## 🏗️ Architecture & Engineering Principles
1. **Offline-First Resilience**: Clinics and homes often have spotty Wi-Fi. The app must never fail during a workout due to network loss. Workouts are logged locally (`localStorage`) and synced when online.
2. **Zero-Bloat Frontend**: Use Vanilla JavaScript, HTML, and CSS. Avoid heavy frontend frameworks (React, Vue, etc.) unless absolutely necessary. The app must load instantly on low-end mobile devices.
3. **Audio is Mission-Critical**: 
   - The 3-Tier Audio Fallback System (Web Speech API -> Cached MP3 -> Live API) must be preserved.
   - All timing is strictly enforced to ensure medical accuracy (e.g., exact 10-second holds).
4. **Mobile-First UI**: The design should be a distraction-free, dark-theme interface optimized entirely for mobile browsers.

## 🛠️ Project Structure & Tech Stack
- **Backend**: Django (Python). Use efficient ORM queries (`select_related`, `prefetch_related`) to prevent bottlenecks.
- **Frontend**: Vanilla JS/CSS. State machines handle player logic and offline queuing.
- **Database**: SQLite (intended for single-tenant/personal use).
- **Audio**: `gTTS` (Google Text-to-Speech) handles bilingual audio (English and Malayalam).

## 🛑 What Not To Do
- **Do not introduce heavy JS frameworks** or complex build tools. Keep it simple.
- **Do not break the audio flow** or the screen WakeLock API. These are core features.
- **Do not clutter the UI**. Maintain a clean, dark mode aesthetic.
- **Do not assume constant internet connection**. Always design for offline fallback.

## 🎯 How to Assist
- **Optimize for Speed**: Ensure the UI is responsive and backend queries are optimized.
- **Enhance the Audio Experience**: Make timing more accurate and transitions smoother.
- **Improve Reliability**: Focus on robust state management and sync logic.
