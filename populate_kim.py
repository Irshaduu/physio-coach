import os
import random
import django
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rehabloop.settings')
django.setup()

from django.contrib.auth.models import User
from workout.models import WorkoutSession, Exercise, ExerciseLog

def get_day_performance(day_index):
    if day_index == 0:
        return random.randint(5, 10)
    elif day_index == 1:
        return random.randint(50, 60)
    elif day_index == 2:
        return random.randint(60, 90)
    elif day_index == 3:
        return 100
    elif day_index == 4:
        return 20
    elif day_index in [5, 6]:
        return 100
    else: 
        return random.randint(75, 95)

def create_user_and_data(username, password):
    user, created = User.objects.get_or_create(username=username)
    user.set_password(password)
    user.save()
    print(f"\nUser '{username}' ready.")

    WorkoutSession.objects.filter(user=user).delete()
    print(f"Cleared existing sessions for '{username}'.")

    exercises = list(Exercise.objects.all())
    if not exercises:
        print("No exercises found in DB!")
        return

    today = timezone.localdate()
    for i in range(10):
        days_ago = 10 - i
        target_date = today - datetime.timedelta(days=days_ago)
        
        slots = [(9, 30), (14, 0), (19, 45)]
        
        for hour, minute in slots:
            slot_perf = get_day_performance(i)
            if slot_perf not in (100, 20):
                slot_perf = min(100, max(0, slot_perf + random.randint(-5, 5)))
            
            if random.random() < 0.10:
                continue
                
            dt = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time(hour, minute)))
            status = 'completed' if slot_perf > 90 else 'abandoned'
            sess = WorkoutSession.objects.create(user=user, status=status)
            WorkoutSession.objects.filter(id=sess.id).update(started_at=dt, date=target_date)
            sess.refresh_from_db()
            
            # Apply the percentage across ALL exercises so the total session score is correct
            for ex in exercises:
                reps = round((slot_perf / 100) * ex.reps)
                if reps > 0:
                    ExerciseLog.objects.create(session=sess, exercise=ex, reps_completed=reps)

    print(f"Generated 10 days of customized dummy data for '{username}'.")

if __name__ == "__main__":
    create_user_and_data("Kim", "123")
    create_user_and_data("kim", "123")
