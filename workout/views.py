import io
import json
import datetime
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm

from .models import Exercise, WorkoutSession, ExerciseLog


# ─── TTS Endpoint (Google Text-to-Speech via gTTS) ──────────────────────────
@csrf_exempt
def tts_api(request):
    """Convert text to speech using gTTS, cache it, and stream back as MP3."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        body = json.loads(request.body)
        text = body.get('text', '').strip()
        lang = body.get('lang', 'en')  # 'ml' or 'en'

        if not text:
            return JsonResponse({'error': 'No text'}, status=400)

        # Create a cache key using MD5 hash of text and lang
        import hashlib
        import os
        from django.conf import settings
        
        cache_dir = os.path.join(settings.BASE_DIR, 'media', 'tts_cache')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            
        filename = hashlib.md5(f"{lang}_{text}".encode('utf-8')).hexdigest() + ".mp3"
        filepath = os.path.join(cache_dir, filename)

        # If cached, serve immediately
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                return HttpResponse(f.read(), content_type='audio/mpeg')

        # Storage Optimization: Keep cache size under 200 files
        try:
            cached_files = [os.path.join(cache_dir, f) for f in os.listdir(cache_dir) if f.endswith('.mp3')]
            if len(cached_files) > 200:
                # Sort by modification time (oldest first)
                cached_files.sort(key=os.path.getmtime)
                # Delete oldest 50 files
                for old_file in cached_files[:50]:
                    try:
                        os.remove(old_file)
                    except OSError:
                        pass
        except Exception as e:
            print(f"Cache cleanup failed: {e}")

        # Map our lang codes to gTTS lang codes
        gtts_lang = 'ml' if lang == 'ml' else 'en'

        from gtts import gTTS
        tts = gTTS(text=text, lang=gtts_lang, slow=False)

        # Write to file for future use
        tts.save(filepath)

        # Stream back the newly generated file
        with open(filepath, 'rb') as f:
            return HttpResponse(f.read(), content_type='audio/mpeg')

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def player(request):
    """Render the main workout player page."""
    exercises = list(
        Exercise.objects.values(
            'id', 'name', 'name_ml', 'description', 'description_ml', 'order',
            'reps', 'hold_seconds', 'rest_seconds',
        )
    )
    display_name = request.user.first_name.strip() or request.user.username

    date_str = request.GET.get('d')
    if date_str:
        try:
            current_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            current_date = timezone.localdate()
    else:
        current_date = timezone.localdate()

    today = timezone.localdate()
    prev_date = current_date - datetime.timedelta(days=1)
    next_date = current_date + datetime.timedelta(days=1) if current_date < today else None
    show_analysis = 'd' in request.GET

    session_data, slots, daily_score = _build_analysis_context(request.user, current_date)

    return render(request, 'workout/player.html', {
        'exercises': exercises,
        'display_name': display_name,
        'current_date': current_date,
        'prev_date': prev_date,
        'next_date': next_date,
        'daily_score': daily_score,
        'slots': slots,
        'all_sessions': session_data,
        'total_sessions': len(session_data),
        'show_analysis': show_analysis,
    })


def _get_slot_type(hour):
    """Return the time-slot label for a given local hour."""
    if 4 <= hour < 11:
        return 'morning'
    elif 11 <= hour < 18:
        return 'afternoon'
    elif 18 <= hour <= 23:
        return 'evening'
    elif 0 <= hour < 4:
        return 'night'
    return 'other'


def _build_analysis_context(user, current_date):
    """Build the session_data, slots, and daily_score for a given date."""
    sessions = WorkoutSession.objects.filter(
        user=user, date=current_date
    ).order_by('started_at').prefetch_related('logs__exercise')

    session_data = []
    for s in sessions:
        local_start = timezone.localtime(s.started_at)
        stype = _get_slot_type(local_start.hour)
        session_data.append({
            'id': s.id,
            'started_at': s.started_at,
            'status': s.status,
            'percent': s.completion_percent,
            'slot_type': stype,
        })

    # Best session per slot (Morning=0, Afternoon=1, Evening=2)
    slots = [None, None, None]
    for s in sessions:
        local_start = timezone.localtime(s.started_at)
        hour = local_start.hour
        if 4 <= hour < 11:
            slot_idx = 0
        elif 11 <= hour < 18:
            slot_idx = 1
        elif 18 <= hour <= 23:
            slot_idx = 2
        else:
            slot_idx = -1

        if slot_idx != -1:
            percent = s.completion_percent
            if slots[slot_idx] is None or percent > slots[slot_idx]['percent']:
                slots[slot_idx] = {
                    'id': s.id,
                    'started_at': s.started_at,
                    'status': s.status,
                    'percent': percent,
                }

    daily_score = round(sum(s['percent'] if s else 0 for s in slots) / 3)
    return session_data, slots, daily_score



def exercises_api(request):
    """Return exercise data as JSON for the frontend engine."""
    exercises = list(
        Exercise.objects.values(
            'id', 'name', 'name_ml', 'description', 'description_ml', 'order',
            'reps', 'hold_seconds', 'rest_seconds',
        )
    )
    return JsonResponse({'exercises': exercises})


@login_required
@csrf_exempt
def sync_session(request):
    """Save or update a workout session and its exercise logs."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
        
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        status = data.get('status', 'in_progress')
        logs = data.get('logs', [])
        
        if session_id:
            session = WorkoutSession.objects.get(id=session_id, user=request.user)
            session.status = status
            if status in ['completed', 'abandoned'] and not session.ended_at:
                session.ended_at = timezone.now()
            session.save()
        else:
            # Only create a session if there's at least one exercise log
            # (i.e. at least 1 exercise was started/completed)
            if not logs:
                return JsonResponse({'session_id': None, 'status': 'no_logs'})
            session = WorkoutSession.objects.create(status=status, user=request.user)
            
        for log_data in logs:
            exercise_id = log_data.get('exercise_id')
            reps = log_data.get('reps_completed', 0)
            if exercise_id:
                # Update or create the log for this exercise
                log, created = ExerciseLog.objects.get_or_create(
                    session=session,
                    exercise_id=exercise_id,
                    defaults={'reps_completed': reps}
                )
                if not created:
                    log.reps_completed = reps
                    log.save()
                    
        return JsonResponse({'session_id': session.id, 'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)



@login_required
def analysis(request):
    """Render the daily analysis dashboard."""
    date_str = request.GET.get('d')
    if date_str:
        try:
            current_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            current_date = timezone.localdate()
    else:
        current_date = timezone.localdate()

    today = timezone.localdate()
    prev_date = current_date - datetime.timedelta(days=1)
    next_date = current_date + datetime.timedelta(days=1) if current_date < today else None

    session_data, slots, daily_score = _build_analysis_context(request.user, current_date)
    display_name = request.user.first_name.strip() or request.user.username

    return render(request, 'workout/analysis.html', {
        'display_name': display_name,
        'current_date': current_date,
        'prev_date': prev_date,
        'next_date': next_date,
        'daily_score': daily_score,
        'slots': slots,
        'all_sessions': session_data,
        'total_sessions': len(session_data),
    })


@login_required
def performance_api(request):
    """Return all-time daily performance scores as JSON for the chart."""
    from collections import defaultdict

    sessions = WorkoutSession.objects.filter(
        user=request.user
    ).order_by('date', 'started_at').prefetch_related('logs__exercise')

    days_sessions = defaultdict(list)
    for s in sessions:
        days_sessions[s.date].append(s)

    data = []
    for date in sorted(days_sessions.keys()):
        day_sessions = days_sessions[date]

        # Best-session-per-slot logic (same as _build_analysis_context)
        slot_bests = [None, None, None]
        for s in day_sessions:
            local_start = timezone.localtime(s.started_at)
            hour = local_start.hour
            if 4 <= hour < 11:
                idx = 0
            elif 11 <= hour < 18:
                idx = 1
            elif 18 <= hour <= 23:
                idx = 2
            else:
                idx = -1

            if idx != -1:
                pct = s.completion_percent
                if slot_bests[idx] is None or pct > slot_bests[idx]:
                    slot_bests[idx] = pct

        daily_score = round(sum(v if v else 0 for v in slot_bests) / 3)
        data.append({
            'date': date.isoformat(),
            'score': daily_score,
            'sessions': len(day_sessions),
        })

    return JsonResponse({'days': data, 'display_name': request.user.first_name.strip() or request.user.username})

@login_required
def reports(request):
    """Render the progress reports page."""
    display_name = request.user.first_name.strip() or request.user.username
    return render(request, 'workout/reports.html', {
        'display_name': display_name,
    })


# ─── Authentication Views ─────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('workout:player')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Link any existing sessions that don't have a user to this first registered user
            # This preserves data for the person who built the app initially
            WorkoutSession.objects.filter(user__isnull=True).update(user=user)
            
            login(request, user)
            return redirect('workout:player')
    else:
        form = UserRegistrationForm()
        
    return render(request, 'workout/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('workout:player')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('workout:player')
    else:
        form = AuthenticationForm()
        
    return render(request, 'workout/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('workout:login')
    # If GET, redirect to player (which will redirect to login if logged out)
    return redirect('workout:player')
