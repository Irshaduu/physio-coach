"""
Tests for the PhysioCoach workout app.

Covers: Models, Views, Forms, APIs, Authentication, and Edge Cases.
Run with: python manage.py test workout
"""
import json
import datetime

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache

from .models import Exercise, WorkoutSession, ExerciseLog
from .forms import UserRegistrationForm
from .views import DEMO_SLOTS, _demo_plan


# =============================================================================
# Helpers
# =============================================================================

def _create_exercises(count=3):
    """Create a set of test exercises and return them as a list.
    
    Uses order starting at 10 to avoid conflicts with the seed
    migration (0006) which populates orders 1-9.
    """
    exercises = []
    for i in range(1, count + 1):
        exercises.append(Exercise.objects.create(
            name=f"Exercise {i}",
            name_ml=f"വ്യായാമം {i}",
            description=f"Description for exercise {i}",
            description_ml=f"വിവരണം {i}",
            order=10 + i,  # Avoid conflict with seeded exercises (1-9)
            reps=20,
            hold_seconds=10,
            rest_seconds=5,
        ))
    return exercises



def _create_user(username='testuser', password='testpass123'):
    """Create and return a test user."""
    return User.objects.create_user(username=username, password=password)


def _create_session(user, status='completed', date=None):
    """Create a workout session for the given user."""
    session = WorkoutSession.objects.create(user=user, status=status)
    if date:
        # Override auto_now_add by updating directly
        WorkoutSession.objects.filter(pk=session.pk).update(date=date)
        session.refresh_from_db()
    return session


# =============================================================================
# Model Tests
# =============================================================================

class ExerciseModelTest(TestCase):
    """Tests for the Exercise model."""

    def test_str_representation(self):
        ex = Exercise.objects.create(name="Quad Sets", order=50)
        self.assertEqual(str(ex), "50. Quad Sets")

    def test_ordering_by_order_field(self):
        Exercise.objects.create(name="Third", order=53)
        Exercise.objects.create(name="First", order=51)
        Exercise.objects.create(name="Second", order=52)
        # Filter to only our test exercises (order > 50)
        names = list(Exercise.objects.filter(order__gte=51).values_list('name', flat=True))
        self.assertEqual(names, ["First", "Second", "Third"])

    def test_order_is_unique(self):
        Exercise.objects.create(name="A", order=60)
        with self.assertRaises(Exception):
            Exercise.objects.create(name="B", order=60)

    def test_default_values(self):
        ex = Exercise.objects.create(name="Test", order=61)
        self.assertEqual(ex.reps, 20)
        self.assertEqual(ex.hold_seconds, 10)
        self.assertEqual(ex.rest_seconds, 5)

    def test_blank_fields_allowed(self):
        """Malayalam fields and description are optional."""
        ex = Exercise.objects.create(name="Test", order=62)
        self.assertEqual(ex.name_ml, '')
        self.assertEqual(ex.description, '')
        self.assertEqual(ex.description_ml, '')


class WorkoutSessionModelTest(TestCase):
    """Tests for the WorkoutSession model."""

    def setUp(self):
        self.user = _create_user()
        self.exercises = _create_exercises(3)
        cache.clear()

    def test_str_representation(self):
        session = _create_session(self.user)
        self.assertIn("Session", str(session))
        self.assertIn("completed", str(session))

    def test_default_status_is_in_progress(self):
        session = WorkoutSession.objects.create(user=self.user)
        self.assertEqual(session.status, 'in_progress')

    def test_completion_percent_no_logs(self):
        session = _create_session(self.user)
        self.assertEqual(session.completion_percent, 0)

    def test_completion_percent_partial(self):
        """One test exercise fully done, total reps = all exercises in DB."""
        session = _create_session(self.user)
        ExerciseLog.objects.create(
            session=session, exercise=self.exercises[0], reps_completed=20
        )
        # 20 reps done out of (9 seeded × 20 + 3 test × 20) = 240 total
        total_reps = sum(e.reps for e in Exercise.objects.all())
        expected = min(100, round((20 / total_reps) * 100))
        self.assertEqual(session.completion_percent, expected)

    def test_completion_percent_full(self):
        """All exercises in DB fully done → 100%."""
        session = _create_session(self.user)
        for ex in Exercise.objects.all():
            ExerciseLog.objects.create(
                session=session, exercise=ex, reps_completed=ex.reps
            )
        self.assertEqual(session.completion_percent, 100)

    def test_completion_percent_caps_at_100(self):
        """Over-completing should still cap at 100%."""
        session = _create_session(self.user)
        for ex in Exercise.objects.all():
            ExerciseLog.objects.create(
                session=session, exercise=ex, reps_completed=ex.reps + 10
            )
        self.assertEqual(session.completion_percent, 100)

    def test_session_ordering(self):
        """Sessions should be ordered by most recent first."""
        s1 = _create_session(self.user)
        s2 = _create_session(self.user)
        sessions = list(WorkoutSession.objects.all())
        self.assertEqual(sessions[0].pk, s2.pk)

    def test_user_cascade_delete(self):
        """Deleting a user should delete their sessions."""
        _create_session(self.user)
        self.assertEqual(WorkoutSession.objects.count(), 1)
        self.user.delete()
        self.assertEqual(WorkoutSession.objects.count(), 0)


class ExerciseLogModelTest(TestCase):
    """Tests for the ExerciseLog model."""

    def setUp(self):
        self.user = _create_user()
        self.exercises = _create_exercises(3)
        self.session = _create_session(self.user)
        cache.clear()

    def test_str_representation(self):
        log = ExerciseLog.objects.create(
            session=self.session, exercise=self.exercises[0], reps_completed=15
        )
        self.assertIn("Exercise 1", str(log))
        self.assertIn("15/20", str(log))

    def test_unique_together_constraint(self):
        """Can't log the same exercise twice in one session."""
        ExerciseLog.objects.create(
            session=self.session, exercise=self.exercises[0], reps_completed=10
        )
        with self.assertRaises(Exception):
            ExerciseLog.objects.create(
                session=self.session, exercise=self.exercises[0], reps_completed=5
            )

    def test_completion_percent(self):
        log = ExerciseLog.objects.create(
            session=self.session, exercise=self.exercises[0], reps_completed=10
        )
        self.assertEqual(log.completion_percent, 50)

    def test_completion_percent_zero_reps_exercise(self):
        """An exercise with 0 reps should return 0% (not divide by zero)."""
        ex = Exercise.objects.create(name="Rest", order=70, reps=0)
        log = ExerciseLog.objects.create(
            session=self.session, exercise=ex, reps_completed=0
        )
        self.assertEqual(log.completion_percent, 0)

    def test_ordering_by_exercise_order(self):
        ExerciseLog.objects.create(
            session=self.session, exercise=self.exercises[2], reps_completed=5
        )
        ExerciseLog.objects.create(
            session=self.session, exercise=self.exercises[0], reps_completed=5
        )
        logs = list(self.session.logs.all())
        self.assertEqual(logs[0].exercise.order, 11)  # exercises[0] has order=10+1
        self.assertEqual(logs[1].exercise.order, 13)  # exercises[2] has order=10+3


# =============================================================================
# Form Tests
# =============================================================================

class UserRegistrationFormTest(TestCase):
    """Tests for the UserRegistrationForm."""

    def test_valid_form(self):
        form = UserRegistrationForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        })
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        form = UserRegistrationForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'pass123',
            'password_confirm': 'different',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password_confirm', form.errors)

    def test_email_is_optional(self):
        form = UserRegistrationForm(data={
            'username': 'newuser',
            'email': '',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        })
        self.assertTrue(form.is_valid())

    def test_duplicate_username_rejected(self):
        _create_user('existing')
        form = UserRegistrationForm(data={
            'username': 'existing',
            'email': '',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        })
        self.assertFalse(form.is_valid())

    def test_save_hashes_password(self):
        form = UserRegistrationForm(data={
            'username': 'hashtest',
            'email': '',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        })
        user = form.save()
        # Password should be hashed, not stored as plain text
        self.assertNotEqual(user.password, 'securepass123')
        self.assertTrue(user.check_password('securepass123'))


# =============================================================================
# Authentication View Tests
# =============================================================================

class AuthViewsTest(TestCase):
    """Tests for login, logout, and registration views."""

    def setUp(self):
        self.client = Client()
        self.user = _create_user()

    def test_login_page_renders(self):
        response = self.client.get(reverse('workout:login'))
        self.assertEqual(response.status_code, 200)
        # The page title contains "Login" (capitalized)
        self.assertContains(response, 'Log', status_code=200)

    def test_login_with_valid_credentials(self):
        response = self.client.post(reverse('workout:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertRedirects(response, reverse('workout:player'))

    def test_login_with_invalid_credentials(self):
        response = self.client.post(reverse('workout:login'), {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)  # Re-renders the form

    def test_login_redirects_if_already_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workout:login'))
        self.assertRedirects(response, reverse('workout:player'))

    def test_register_page_renders(self):
        response = self.client.get(reverse('workout:register'))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(reverse('workout:register'), {
            'username': 'newuser',
            'email': '',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        })
        self.assertRedirects(response, reverse('workout:player'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_redirects_if_already_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workout:register'))
        self.assertRedirects(response, reverse('workout:player'))

    def test_logout_requires_post(self):
        self.client.login(username='testuser', password='testpass123')
        # GET should redirect, not log out
        response = self.client.get(reverse('workout:logout'))
        self.assertRedirects(response, reverse('workout:player'))

    def test_logout_via_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('workout:logout'))
        self.assertRedirects(response, reverse('workout:login'))

    def test_register_links_orphan_sessions(self):
        """Registering should claim any user=None sessions."""
        orphan = WorkoutSession.objects.create(user=None, status='completed')
        self.client.post(reverse('workout:register'), {
            'username': 'claimer',
            'email': '',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        })
        orphan.refresh_from_db()
        self.assertEqual(orphan.user.username, 'claimer')


# =============================================================================
# Protected View Tests
# =============================================================================

class ProtectedViewsTest(TestCase):
    """Tests for views that require authentication."""

    def setUp(self):
        self.client = Client()
        self.user = _create_user()
        _create_exercises(3)
        cache.clear()

    def test_player_requires_login(self):
        response = self.client.get(reverse('workout:player'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_player_renders_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workout:player'))
        self.assertEqual(response.status_code, 200)

    def test_player_uses_first_name_if_available(self):
        self.user.first_name = 'Irshad'
        self.user.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workout:player'))
        self.assertContains(response, 'Irshad')

    def test_player_falls_back_to_username(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workout:player'))
        self.assertContains(response, 'testuser')

    def test_analysis_requires_login(self):
        response = self.client.get(reverse('workout:analysis'))
        self.assertEqual(response.status_code, 302)

    def test_analysis_renders_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workout:analysis'))
        self.assertEqual(response.status_code, 200)

    def test_reports_requires_login(self):
        response = self.client.get(reverse('workout:reports'))
        self.assertEqual(response.status_code, 302)

    def test_reports_renders_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workout:reports'))
        self.assertEqual(response.status_code, 200)

    def test_player_with_date_param(self):
        """Player should accept a ?d=YYYY-MM-DD query param."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workout:player') + '?d=2026-01-15')
        self.assertEqual(response.status_code, 200)

    def test_player_with_invalid_date_falls_back_to_today(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workout:player') + '?d=not-a-date')
        self.assertEqual(response.status_code, 200)

    def test_analysis_with_invalid_date_falls_back_to_today(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workout:analysis') + '?d=invalid')
        self.assertEqual(response.status_code, 200)


# =============================================================================
# API Tests
# =============================================================================

class ExercisesAPITest(TestCase):
    """Tests for the exercises JSON endpoint."""

    def setUp(self):
        _create_exercises(3)

    def test_returns_json(self):
        response = self.client.get(reverse('workout:exercises_api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_returns_all_exercises(self):
        response = self.client.get(reverse('workout:exercises_api'))
        data = response.json()
        # 9 seeded exercises + 3 test exercises = 12
        self.assertEqual(len(data['exercises']), 12)

    def test_exercise_fields_present(self):
        response = self.client.get(reverse('workout:exercises_api'))
        ex = response.json()['exercises'][0]
        expected_fields = ['id', 'name', 'name_ml', 'description',
                           'description_ml', 'order', 'reps',
                           'hold_seconds', 'rest_seconds']
        for field in expected_fields:
            self.assertIn(field, ex)

    def test_exercises_api_is_public(self):
        """Exercises endpoint doesn't require login (feeds the service worker)."""
        response = self.client.get(reverse('workout:exercises_api'))
        self.assertEqual(response.status_code, 200)


class SyncSessionAPITest(TestCase):
    """Tests for the session sync endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = _create_user()
        self.exercises = _create_exercises(3)
        cache.clear()

    def test_requires_login(self):
        response = self.client.post(
            reverse('workout:sync_session'),
            data=json.dumps({'status': 'completed', 'logs': []}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 302)

    def test_rejects_get_request(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workout:sync_session'))
        self.assertEqual(response.status_code, 405)

    def test_create_new_session_with_logs(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('workout:sync_session'),
            data=json.dumps({
                'status': 'completed',
                'logs': [
                    {'exercise_id': self.exercises[0].id, 'reps_completed': 20},
                    {'exercise_id': self.exercises[1].id, 'reps_completed': 15},
                ],
            }),
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIsNotNone(data['session_id'])

        # Verify the session and logs were created
        session = WorkoutSession.objects.get(id=data['session_id'])
        self.assertEqual(session.status, 'completed')
        self.assertEqual(session.logs.count(), 2)

    def test_no_session_created_without_logs(self):
        """Empty logs array should not create a session."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('workout:sync_session'),
            data=json.dumps({'status': 'completed', 'logs': []}),
            content_type='application/json',
        )
        data = response.json()
        self.assertIsNone(data['session_id'])
        self.assertEqual(WorkoutSession.objects.count(), 0)

    def test_update_existing_session(self):
        self.client.login(username='testuser', password='testpass123')
        session = _create_session(self.user, status='in_progress')
        response = self.client.post(
            reverse('workout:sync_session'),
            data=json.dumps({
                'session_id': session.id,
                'status': 'completed',
                'logs': [
                    {'exercise_id': self.exercises[0].id, 'reps_completed': 20},
                ],
            }),
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(data['status'], 'success')
        session.refresh_from_db()
        self.assertEqual(session.status, 'completed')
        self.assertIsNotNone(session.ended_at)

    def test_update_reps_on_existing_log(self):
        """Syncing the same exercise twice should update, not duplicate."""
        self.client.login(username='testuser', password='testpass123')
        session = _create_session(self.user)
        ExerciseLog.objects.create(
            session=session, exercise=self.exercises[0], reps_completed=5
        )
        self.client.post(
            reverse('workout:sync_session'),
            data=json.dumps({
                'session_id': session.id,
                'status': 'completed',
                'logs': [
                    {'exercise_id': self.exercises[0].id, 'reps_completed': 20},
                ],
            }),
            content_type='application/json',
        )
        log = ExerciseLog.objects.get(session=session, exercise=self.exercises[0])
        self.assertEqual(log.reps_completed, 20)

    def test_cannot_update_another_users_session(self):
        """Should fail if a user tries to sync another user's session."""
        other_user = _create_user('other', 'otherpass123')
        session = _create_session(other_user)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('workout:sync_session'),
            data=json.dumps({
                'session_id': session.id,
                'status': 'completed',
                'logs': [],
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_malformed_json_returns_400(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('workout:sync_session'),
            data='not json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


class TTSAPITest(TestCase):
    """Tests for the text-to-speech endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = _create_user()

    def test_requires_authentication(self):
        response = self.client.post(
            reverse('workout:tts_api'),
            data=json.dumps({'text': 'hello', 'lang': 'en'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    def test_rejects_get_request(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workout:tts_api'))
        self.assertEqual(response.status_code, 405)

    def test_rejects_empty_text(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('workout:tts_api'),
            data=json.dumps({'text': '', 'lang': 'en'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


class PerformanceAPITest(TestCase):
    """Tests for the performance chart data endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = _create_user()
        self.exercises = _create_exercises(3)
        cache.clear()

    def test_requires_login(self):
        response = self.client.get(reverse('workout:performance_api'))
        self.assertEqual(response.status_code, 302)

    def test_returns_empty_for_new_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workout:performance_api'))
        data = response.json()
        self.assertEqual(data['days'], [])

    def test_returns_daily_scores(self):
        self.client.login(username='testuser', password='testpass123')
        session = _create_session(self.user)
        for ex in self.exercises:
            ExerciseLog.objects.create(
                session=session, exercise=ex, reps_completed=ex.reps
            )
        response = self.client.get(reverse('workout:performance_api'))
        data = response.json()
        self.assertGreater(len(data['days']), 0)
        self.assertIn('score', data['days'][0])
        self.assertIn('date', data['days'][0])

    def test_includes_display_name(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workout:performance_api'))
        data = response.json()
        self.assertEqual(data['display_name'], 'testuser')


# =============================================================================
# Edge Case & Slot Logic Tests
# =============================================================================

class SlotLogicTest(TestCase):
    """Tests for the time-slot classification and daily score logic."""

    def test_morning_slot(self):
        from .views import _get_slot_type
        self.assertEqual(_get_slot_type(4), 'morning')
        self.assertEqual(_get_slot_type(10), 'morning')

    def test_afternoon_slot(self):
        from .views import _get_slot_type
        self.assertEqual(_get_slot_type(11), 'afternoon')
        self.assertEqual(_get_slot_type(17), 'afternoon')

    def test_evening_slot(self):
        from .views import _get_slot_type
        self.assertEqual(_get_slot_type(18), 'evening')
        self.assertEqual(_get_slot_type(23), 'evening')

    def test_night_slot(self):
        from .views import _get_slot_type
        self.assertEqual(_get_slot_type(0), 'night')
        self.assertEqual(_get_slot_type(3), 'night')

    def test_daily_score_with_no_sessions(self):
        """An empty day should have a daily score of 0."""
        from .views import _build_analysis_context
        user = _create_user()
        _, _, daily_score = _build_analysis_context(user, timezone.localdate())
        self.assertEqual(daily_score, 0)


# =============================================================================
# URL Routing Tests
# =============================================================================

class URLRoutingTest(TestCase):
    """Verify all URL patterns resolve correctly."""

    def test_player_url(self):
        self.assertEqual(reverse('workout:player'), '/')

    def test_analysis_url(self):
        self.assertEqual(reverse('workout:analysis'), '/analysis/')

    def test_reports_url(self):
        self.assertEqual(reverse('workout:reports'), '/reports/')

    def test_exercises_api_url(self):
        self.assertEqual(reverse('workout:exercises_api'), '/api/exercises/')

    def test_sync_api_url(self):
        self.assertEqual(reverse('workout:sync_session'), '/api/sync/')

    def test_tts_api_url(self):
        self.assertEqual(reverse('workout:tts_api'), '/api/tts/')

    def test_performance_api_url(self):
        self.assertEqual(reverse('workout:performance_api'), '/api/performance/')

    def test_login_url(self):
        self.assertEqual(reverse('workout:login'), '/login/')

    def test_register_url(self):
        self.assertEqual(reverse('workout:register'), '/register/')

    def test_logout_url(self):
        self.assertEqual(reverse('workout:logout'), '/logout/')


# =============================================================================
# Data Isolation Tests
# =============================================================================

class DataIsolationTest(TestCase):
    """Ensure users only see their own data."""

    def setUp(self):
        self.client = Client()
        self.user1 = _create_user('user1', 'pass123')
        self.user2 = _create_user('user2', 'pass123')
        self.exercises = _create_exercises(3)
        cache.clear()

    def test_player_shows_only_own_sessions(self):
        _create_session(self.user1)
        _create_session(self.user2)

        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('workout:player') + '?d=' + timezone.localdate().isoformat())
        # user1 should only see 1 session in context
        self.assertEqual(response.context['total_sessions'], 1)

    def test_performance_api_returns_only_own_data(self):
        session = _create_session(self.user2)
        ExerciseLog.objects.create(
            session=session, exercise=self.exercises[0], reps_completed=20
        )

        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('workout:performance_api'))
        data = response.json()
        self.assertEqual(data['days'], [])


# =============================================================================
# One-tap Demo
# =============================================================================

class DemoViewTest(TestCase):
    """The demo signs in a throwaway guest with ten days of sample progress."""

    def setUp(self):
        self.client = Client()
        cache.clear()

    def _guest(self):
        return User.objects.get(groups__name='Demo guests')

    def test_demo_signs_in_a_guest_and_opens_the_player(self):
        response = self.client.post(reverse('workout:demo'))
        self.assertRedirects(response, reverse('workout:player'))
        guest = self._guest()
        self.assertTrue(guest.username.startswith('guest-'))
        self.assertEqual(guest.first_name, 'Guest')
        self.assertFalse(guest.has_usable_password())
        self.assertEqual(int(self.client.session['_auth_user_id']), guest.id)

    def test_demo_seeds_ten_past_days_that_improve(self):
        self.client.post(reverse('workout:demo'))
        days = self.client.get(reverse('workout:performance_api')).json()['days']
        today = timezone.localdate()
        dates = [datetime.date.fromisoformat(d['date']) for d in days]
        self.assertEqual(len(dates), 10)
        self.assertTrue(all(today - datetime.timedelta(days=10) <= d < today for d in dates))
        scores = [d['score'] for d in days]
        self.assertGreaterEqual(scores[-1], 85)
        self.assertGreaterEqual(scores[-1] - scores[0], 40)
        self.assertGreaterEqual(sum(s >= 70 for s in scores), 4)  # the report's "good days"

    def test_demo_leaves_today_for_the_visitor(self):
        self.client.post(reverse('workout:demo'))
        guest = self._guest()
        self.assertFalse(WorkoutSession.objects.filter(user=guest, date=timezone.localdate()).exists())

    def test_demo_needs_a_post(self):
        response = self.client.get(reverse('workout:demo'))
        self.assertRedirects(response, reverse('workout:login'))
        self.assertFalse(User.objects.exists())

    def test_demo_is_limited_per_address(self):
        for _ in range(10):
            self.client.post(reverse('workout:demo'))
            self.client.post(reverse('workout:logout'))
        response = self.client.post(reverse('workout:demo'))
        self.assertEqual(response.status_code, 429)
        self.assertContains(response, 'Too many demo accounts', status_code=429)
        self.assertEqual(User.objects.filter(groups__name='Demo guests').count(), 10)

    def test_yesterdays_guests_are_deleted_with_their_sessions(self):
        self.client.post(reverse('workout:demo'))
        old = self._guest()
        User.objects.filter(pk=old.pk).update(date_joined=timezone.now() - datetime.timedelta(days=2))
        real = _create_user('asha', 'pass123')
        User.objects.filter(pk=real.pk).update(date_joined=timezone.now() - datetime.timedelta(days=30))
        _create_session(real)
        self.client.post(reverse('workout:logout'))

        self.client.post(reverse('workout:demo'))
        self.assertFalse(User.objects.filter(pk=old.pk).exists())
        self.assertFalse(WorkoutSession.objects.filter(user_id=old.pk).exists())
        self.assertTrue(WorkoutSession.objects.filter(user=real).exists())

    def test_signed_in_user_goes_straight_to_the_player(self):
        _create_user('asha', 'pass123')
        self.client.login(username='asha', password='pass123')
        response = self.client.post(reverse('workout:demo'))
        self.assertRedirects(response, reverse('workout:player'))
        self.assertFalse(User.objects.filter(groups__name='Demo guests').exists())

    def test_login_and_register_pages_offer_the_demo(self):
        for name in ('workout:login', 'workout:register'):
            self.assertContains(self.client.get(reverse(name)), 'Try the demo')

    def test_guest_sees_the_player_by_name(self):
        self.client.post(reverse('workout:demo'))
        response = self.client.get(reverse('workout:player'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Guest')


class DemoPlanTest(TestCase):
    """Every guest's sample progress reads as a recovery, whatever their id draws."""

    def _scores(self, seed):
        # Scored as the report does: the mean of the three slots, a missed slot counting as zero.
        days = {}
        for days_ago, slot, pct in _demo_plan(seed):
            days.setdefault(days_ago, [0, 0, 0])[DEMO_SLOTS.index(slot)] = pct
        return [round(sum(days[d]) / 3) for d in range(10, 0, -1)]

    def test_every_guest_ends_high_after_a_real_climb(self):
        for seed in range(1, 501):
            scores = self._scores(seed)
            self.assertGreaterEqual(scores[-1], 85, seed)
            self.assertLessEqual(scores[0], 50, seed)
            self.assertGreaterEqual(sum(s >= 70 for s in scores), 4, seed)

    def test_one_missed_session_in_the_first_days(self):
        for seed in range(1, 501):
            plan = _demo_plan(seed)
            self.assertEqual(len(plan), 29, seed)
            have = {(days_ago, slot) for days_ago, slot, _ in plan}
            missed = [(d, s) for d in range(1, 11) for s in DEMO_SLOTS if (d, s) not in have]
            self.assertEqual(len(missed), 1, seed)
            self.assertGreaterEqual(missed[0][0], 7, seed)

    def test_same_guest_same_progress(self):
        self.assertEqual(_demo_plan(42), _demo_plan(42))
