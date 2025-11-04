# goals/tests/test_freeze_on_view.py
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone
from courses.models import Course
from goals.models import Goal, GoalOutcome
from goals.services import last_week_range
from study_sessions.models import StudySession


@override_settings(TIME_ZONE="Europe/London", USE_TZ=True)
class WeeklyFreezeOnViewTests(TestCase):
    @patch("goals.services.timezone.now")
    def test_goal_detail_triggers_weekly_freeze_on_monday(self, mock_now):
        # Pretend "now" is Monday 2025-11-03 09:00 Europe/London
        mock_now.return_value = datetime(2025, 11, 3, 9, 0, tzinfo=ZoneInfo("Europe/London"))

        User = get_user_model()
        user = User.objects.create_user(username="teresa", email="t@example.com", password="pw")
        course = Course.objects.create(title="Demo Course", owner=user,)
             
        # Minimal goal with a 1.5h weekly target
        goal = Goal.objects.create(user=user, weekly_hours_target=Decimal("1.5"), course=course)

        # Work out last week's window using the same service helper your app uses
        ws, we = last_week_range(today=mock_now.return_value.date())
        start_dt = timezone.make_aware(datetime(ws.year, ws.month, ws.day, 10, 0), ZoneInfo("Europe/London"))

        # Two study sessions last week: 90 + 30 minutes = 120 mins = 2.0 hours
        StudySession.objects.create(user=user, goal=goal, course=course, duration_minutes=90, started_at=start_dt)
        StudySession.objects.create(user=user, goal=goal, course=course, duration_minutes=30, started_at=start_dt + timedelta(days=2))
        
        # Hit the goal detail view, which calls freeze_weekly_outcomes(...)
        client = Client()
        client.force_login(user)

        url = reverse("goals:detail", args=[goal.pk])
        resp = client.get(url)
        self.assertEqual(resp.status_code, 200)

        # Assert a GoalOutcome for last week now exists and is correct
        self.assertTrue(GoalOutcome.objects.filter(goal=goal, week_start=ws).exists())
        outcome = GoalOutcome.objects.get(goal=goal, week_start=ws)
        self.assertEqual(outcome.hours_completed, Decimal("2.0"))  # 120 mins → 2.0h
        self.assertTrue(outcome.completed)  # 2.0h >= 1.5h target

        # Idempotent: hitting the page again does not create duplicates
        client.get(url)
        self.assertEqual(GoalOutcome.objects.filter(goal=goal, week_start=ws).count(), 1)
