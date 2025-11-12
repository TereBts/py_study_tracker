"""Goal outcome freezing services.

Provides utilities to compute ISO week ranges and to freeze per-goal weekly
progress into GoalOutcome snapshots. Intended to run via a scheduled job
(e.g., every Monday in Europe/London) or manually with explicit dates.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Tuple

from django.db import models, transaction
from django.utils import timezone

from .models import Goal, GoalOutcome
from study_sessions.models import StudySession
from zoneinfo import ZoneInfo
from datetime import date, timedelta


def _monday_of_week(d: date) -> date:
    """
    Return the Monday (ISO week start) for the given date.

    Args:
        d (date): Any date within the week.

    Returns:
        date: The Monday of that ISO week.
    """
    return d - timedelta(days=d.weekday())


def _sunday_of_week(monday: date) -> date:
    """
    Return the Sunday (ISO week end) for the given Monday.

    Args:
        monday (date): A date that is a Monday.

    Returns:
        date: The Sunday of that ISO week.
    """
    return monday + timedelta(days=6)


def last_week_range(today: Optional[date] = None) -> Tuple[date, date]:
    """
    Compute the (Monday, Sunday) date range for the previous ISO week.

    If `today` is omitted, uses the local date from Django's timezone
    utilities.

    Args:
        today (Optional[date]): Anchor date to calculate from. Defaults to
        local today.

    Returns:
        Tuple[date, date]: (week_start_monday, week_end_sunday) for last week.
    """
    base = timezone.localdate() if today is None else today
    one_week_ago = base - timedelta(days=7)
    start = _monday_of_week(one_week_ago)
    end = _sunday_of_week(start)
    return start, end


@transaction.atomic
def freeze_weekly_outcomes(
    week_start: Optional[date] = None,
    week_end: Optional[date] = None,
    dry_run: bool = False,
) -> dict:
    """
    Summarise a week's study activity into GoalOutcome snapshots for active
    goals.

    By default (when week_start/week_end are not supplied), this function
    only performs work on **Mondays** in the **Europe/London** timezone.
    It then freezes the *previous* ISO week (Mon–Sun). If explicit dates
    are provided, it operates for that week regardless of the current day.

    For each active Goal, it:
      - Sums StudySession.duration_minutes for the week and converts to hours
      (1 dp).
      - Approximates lessons_completed via session count (if one session ≈ one
      lesson).
      - Marks `completed=True` if either weekly_hours_target or
      weekly_lessons_target is met.
      - Upserts (update_or_create) a GoalOutcome for (goal, week_start).

    Args:
        week_start (Optional[date]): Monday of the week to freeze. If None,
        inferred.
        week_end (Optional[date]): Sunday of the week to freeze. If None,
        inferred.
        dry_run (bool): If True, prints what would be written without touching
        the DB.

    Returns:
        dict: A summary with keys:
            - "created" (int): Number of GoalOutcome rows created.
            - "updated" (int): Number of GoalOutcome rows updated.
            - "week_start" (date | None): The effective Monday used (or None
            if skipped).
            - "week_end" (date | None): The effective Sunday used (or None if
            skipped).
    """
    today_local = timezone.now().astimezone(ZoneInfo("Europe/London")).date()

    # Only run automatically on Mondays, unless explicit range is provided
    if today_local.weekday() != 0 and not (week_start and week_end):
        return {"created": 0, "updated": 0, "week_start": None, "week_end":
                None}

    if not week_start or not week_end:
        week_start, week_end = last_week_range()

    created, updated = 0, 0

    for goal in Goal.objects.filter(is_active=True):
        # Filter sessions by goal and date range (inclusive)
        sessions = StudySession.objects.filter(
            goal=goal,
            started_at__date__gte=week_start,
            started_at__date__lte=week_end,
        )

        # ---- HOURS (from minutes) ----
        total_minutes = (
            sessions.aggregate(total=models.Sum("duration_minutes"))["total"]
            or 0
            )
        hours = (Decimal(total_minutes) / Decimal(60)).quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        )

        # ---- LESSONS (proxy by session count) ----
        lessons_count = sessions.count()

        # ---- Targets & completion (robust to Decimal/float/None) ----
        hours_target_raw = getattr(goal, "weekly_hours_target", None)
        lessons_target_raw = getattr(goal, "weekly_lessons_target", None)

        hours_target = None
        if hours_target_raw is not None:
            # Normalize to Decimal safely even if model gives float
            hours_target = Decimal(str(hours_target_raw))

        lessons_target = None
        if lessons_target_raw is not None:
            lessons_target = int(lessons_target_raw)

        completed = False
        if hours_target is not None and hours >= hours_target:
            completed = True
        if lessons_target is not None and lessons_count >= lessons_target:
            completed = True

        data = {
            "hours_completed": hours,
            "lessons_completed": lessons_count,
            "hours_target": hours_target_raw,
            "lessons_target": lessons_target_raw,
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
