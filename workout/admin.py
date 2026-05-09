from django.contrib import admin
from .models import Exercise, WorkoutSession, ExerciseLog


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'reps', 'hold_seconds', 'rest_seconds')
    ordering = ('order',)


class ExerciseLogInline(admin.TabularInline):
    model = ExerciseLog
    extra = 0


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ('date', 'started_at', 'status', 'completion_percent')
    list_filter = ('status', 'date')
    inlines = [ExerciseLogInline]
