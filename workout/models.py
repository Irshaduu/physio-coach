from django.db import models
from django.contrib.auth.models import User


class Exercise(models.Model):
    """A single physiotherapy exercise in the routine."""
    name = models.CharField(max_length=100)
    name_ml = models.CharField(max_length=100, blank=True)
    description = models.TextField(
        blank=True,
        help_text="Brief instruction or cue for the exercise (English)."
    )
    description_ml = models.TextField(
        blank=True,
        help_text="Brief instruction or cue for the exercise (Malayalam)."
    )
    order = models.PositiveSmallIntegerField(
        unique=True,
        help_text="Position in the workout sequence (1-9)."
    )
    reps = models.PositiveSmallIntegerField(default=20)
    hold_seconds = models.PositiveSmallIntegerField(default=10)
    rest_seconds = models.PositiveSmallIntegerField(default=5)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.name}"


class WorkoutSession(models.Model):
    """Tracks a single workout session for adherence logging."""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='in_progress'
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Session {self.started_at:%Y-%m-%d %H:%M} — {self.status}"

    @property
    def completion_percent(self):
        """Calculates total completion based on actual reps done across all exercises."""
        logs = self.logs.all()
        if not logs:
            return 0
            
        from django.core.cache import cache
        from django.db.models import Sum
        
        total_reps_required = cache.get('total_workout_reps')
        if not total_reps_required:
            total_reps_required = Exercise.objects.aggregate(total=Sum('reps'))['total'] or 1
            cache.set('total_workout_reps', total_reps_required, 60*60*24)
            
        total_reps_completed = sum(log.reps_completed for log in logs)
        
        # Cap at 100% just in case
        percent = (total_reps_completed / total_reps_required) * 100
        return min(100, round(percent))


class ExerciseLog(models.Model):
    """Tracks exactly how many reps were completed for a specific exercise in a session."""
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='logs')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    reps_completed = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        unique_together = ('session', 'exercise')
        ordering = ['exercise__order']
        
    def __str__(self):
        return f"{self.session} - {self.exercise.name}: {self.reps_completed}/{self.exercise.reps}"
        
    @property
    def completion_percent(self):
        if self.exercise.reps == 0:
            return 0
        percent = (self.reps_completed / self.exercise.reps) * 100
        return min(100, round(percent))
