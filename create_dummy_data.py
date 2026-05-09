import os
import random
import django
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rehabloop.settings')
django.setup()

from django.contrib.auth.models import User
from workout.models import WorkoutSession, Exercise, ExerciseLog

def create_10_days_data():
    username = "soo1"
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"User {username} not found.")
        return

    # Delete all previous sessions for this user to have a clean graph
    WorkoutSession.objects.filter(user=user).delete()
    print(f"Cleared all existing sessions for '{username}'.")

    first_ex = Exercise.objects.first()
    if not first_ex:
        print("No exercises found in DB!")
        return

    today = timezone.localdate()
    
    # We will simulate a progressive improvement over 10 days
    # Day 1: ~30%, Day 10: ~95%
    print("Generating 10 days of progress data...")
    
    for i in range(10):
        # Go backwards from yesterday to 10 days ago
        days_ago = 10 - i
        target_date = today - datetime.timedelta(days=days_ago)
        
        # Base performance improves as days go on (from 25% to 90%)
        base_perf = 25 + (i * 7) 
        
        # We'll create 3 slots for each day (Morning, Afternoon, Evening)
        slots = [
            (9, 30),   # Morning
            (14, 0),   # Afternoon
            (19, 45)   # Evening
        ]
        
        daily_logs = 0
        
        for hour, minute in slots:
            # Random variance for each slot (-15% to +15%)
            variance = random.randint(-15, 15)
            slot_perf = min(100, max(0, base_perf + variance))
            
            # Occasionally skip a slot entirely (20% chance)
            if random.random() < 0.20:
                continue
                
            dt = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time(hour, minute)))
            
            # Create session
            status = 'completed' if slot_perf > 90 else 'abandoned'
            sess = WorkoutSession.objects.create(user=user, status=status)
            WorkoutSession.objects.filter(id=sess.id).update(started_at=dt, date=target_date)
            sess.refresh_from_db()
            
            # Create logs
            reps = round((slot_perf / 100) * first_ex.reps)
            if reps > 0:
                ExerciseLog.objects.create(session=sess, exercise=first_ex, reps_completed=reps)
                daily_logs += 1

        print(f"  Day {target_date.strftime('%b %d')}: Base ~{base_perf}% -> created {daily_logs} sessions.")

    print("\nDone! 10 days of performance data generated. Check the Reports graph!")

if __name__ == "__main__":
    create_10_days_data()
