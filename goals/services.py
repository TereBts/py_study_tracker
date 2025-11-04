from datetime import date, timedelta, datetime
from decimal import Decimal, ROUND_HALF_UP
from django.db import models, transaction
from django.utils import timezone
from .models import Goal, GoalOutcome
from study_sessions.models import StudySession 
from zoneinfo import ZoneInfo


def _monday_of_week(d: date) -> date:
    return d - timedelta(days=d.weekday())

def _sunday_of_week(monday: date) -> date:
    return monday + timedelta(days=6)

def last_week_range(today=None):
    """Return (Mon, Sun) for the previous ISO week in local time."""
    base = timezone.localdate() if today is None else today
    one_week_ago = base - timedelta(days=7)
    start = _monday_of_week(one_week_ago)
    end = _sunday_of_week(start)
    return start, end


@transaction.atomic
def freeze_weekly_outcomes(week_start=None, week_end=None, dry_run=False):
    """
    Summarise last week's progress and freeze it into GoalOutcome records.
    Uses StudySession.duration_minutes and converts to hours (1 decimal).
    Only does work automatically on Mondays in Europe/London unless an explicit
    (week_start, week_end) is provided.
    """
    today_local = timezone.now().astimezone(ZoneInfo("Europe/London")).date()
    if today_local.weekday() != 0 and not (week_start and week_end):
        return {"created": 0, "updated": 0, "week_start": None, "week_end": None}

    if not week_start or not week_end:
        week_start, week_end = last_week_range()

    created, updated = 0, 0

    for goal in Goal.objects.filter(is_active=True):
        # Filter sessions by goal and by started_at date range (inclusive)
        sessions = StudySession.objects.filter(
            goal=goal,
            started_at__date__gte=week_start,
            started_at__date__lte=week_end,
        )

        # ---- HOURS (from minutes) ----
        total_minutes = sessions.aggregate(
            total=models.Sum("duration_minutes")
        )["total"] or 0

        # Convert to hours with one decimal place
        hours = (Decimal(total_minutes) / Decimal(60)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

        # ---- LESSONS (best-effort) ----
        # Your StudySession doesn’t have a lessons_completed field.
        # If you log one session per lesson, we can approximate with a count:
        lessons_count = sessions.count()

        # Compute completion: satisfied if either weekly_hours_target OR weekly_lessons_target is met.
        completed = False
        if goal.weekly_hours_target is not None and hours >= Decimal(goal.weekly_hours_target):
            completed = True
        if goal.weekly_lessons_target is not None and lessons_count >= goal.weekly_lessons_target:
            completed = True

        data = {
            "hours_completed": hours,
            "lessons_completed": lessons_count,         # uses count as a proxy
            "hours_target": goal.weekly_hours_target,
            "lessons_target": goal.weekly_lessons_target,
            "completed": completed,
            "week_end": week_end,
        }

        if dry_run:
            print(f"[DRY RUN] {goal} {week_start}–{week_end} → {data}")
            continue

        obj, created_flag = GoalOutcome.objects.update_or_create(
            goal=goal,
            week_start=week_start,
            defaults=data,
        )
        created += int(created_flag)
        updated += int(not created_flag)

    return {
        "created": created,
        "updated": updated,
        "week_start": week_start,
        "week_end": week_end,
    }
