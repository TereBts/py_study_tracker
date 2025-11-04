from datetime import date, datetime, timedelta
from django.db import models, transaction
from django.utils import timezone

from .models import Goal, GoalOutcome
from study_sessions.models import StudySession 


def _monday_of_week(d: date) -> date:
    return d - timedelta(days=d.weekday())  # Monday is 0

def _sunday_of_week(monday: date) -> date:
    return monday + timedelta(days=6)

def last_week_range(today=None):
    """Return Monday–Sunday of the previous week."""
    tz_now = timezone.localdate()
    if today:
        tz_now = today
    one_week_ago = tz_now - timedelta(days=7)
    start = _monday_of_week(one_week_ago)
    end = _sunday_of_week(start)
    return start, end


@transaction.atomic
def freeze_weekly_outcomes(week_start=None, week_end=None, dry_run=False):
    """Summarise last week's progress and freeze it into GoalOutcome records."""
    if not week_start or not week_end:
        week_start, week_end = last_week_range()

    created, updated = 0, 0

    for goal in Goal.objects.filter(is_active=True):
        # sum study time for this goal in the date range
        sessions = StudySession.objects.filter(
            goal=goal,
            started_at__date__gte=week_start,
            started_at__date__lte=week_end,
        )

        total_hours = sessions.aggregate(models.Sum("duration_hours"))["duration_hours__sum"] or 0
        total_lessons = sessions.aggregate(models.Sum("lessons_completed"))["lessons_completed__sum"] or 0

        completed = False
        if goal.weekly_hours_target and total_hours >= goal.weekly_hours_target:
            completed = True
        elif goal.weekly_lessons_target and total_lessons >= goal.weekly_lessons_target:
            completed = True

        data = {
            "hours_completed": total_hours,
            "lessons_completed": total_lessons,
            "hours_target": goal.weekly_hours_target,
            "lessons_target": goal.weekly_lessons_target,
            "completed": completed,
            "week_end": week_end,
        }

        if dry_run:
            print(f"Would save {goal} ({week_start}) → {data}")
            continue

        obj, created_flag = GoalOutcome.objects.update_or_create(
            goal=goal,
            week_start=week_start,
            defaults=data,
        )
        created += int(created_flag)
        updated += int(not created_flag)

    return {"created": created, "updated": updated, "week_start": week_start, "week_end": week_end}
