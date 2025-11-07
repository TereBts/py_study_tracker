from datetime import date

from django.utils import timezone
from django.db.models import Sum

from .models import Achievement, UserAchievement
from study_sessions.models import StudySession
from goals.models import GoalOutcome


def get_user_stats(user):
    """
    Collect basic stats needed for achievement rules.
    """

    # Total study minutes for this user
    total_minutes = (
        StudySession.objects.filter(user=user)
        .aggregate(total=Sum("duration_minutes"))
        .get("total") or 0
    )

    # Number of completed goals for this user
    # We count GoalOutcome rows marked completed=True for goals owned by this user
    completed_goals = GoalOutcome.objects.filter(
        goal__user=user,
        completed=True
    ).count()

    # Weekly streak: consecutive ISO weeks (up to now) where user has at least one session
    sessions = (
        StudySession.objects
        .filter(user=user)
        .values_list("started_at", flat=True)
    )

    weeks_with_study = set()
    for dt in sessions:
        # dt is a datetime; get its date part
        d = dt.date()
        year, week, _ = d.isocalendar()
        weeks_with_study.add((year, week))

    streak = 0
    if weeks_with_study:
        today = timezone.localdate()
        year, week, _ = today.isocalendar()

        # Walk backwards week by week while they have activity
        while (year, week) in weeks_with_study:
            streak += 1
            week -= 1
            if week == 0:
                year -= 1
                # ISO week for last week of previous year
                week = date(year, 12, 28).isocalendar()[1]

    return {
        "total_minutes": total_minutes,
        "completed_goals": completed_goals,
        "weekly_streak_weeks": streak,
    }


def is_eligible(achievement, stats):
    """
    Decide if the user matches this achievement based on rule_type & rule_params.
    """
    p = achievement.rule_params or {}

    if achievement.rule_type == "total_hours":
        threshold_hours = p.get("threshold", 0)
        return stats["total_minutes"] >= threshold_hours * 60

    if achievement.rule_type == "goals_completed":
        threshold = p.get("threshold", 0)
        return stats["completed_goals"] >= threshold

    if achievement.rule_type == "weekly_streak":
        needed_weeks = p.get("weeks", 0)
        return stats["weekly_streak_weeks"] >= needed_weeks

    # Unknown rule types currently evaluate to False
    return False


def evaluate_achievements_for_user(user):
    """
    Check all achievements for this user and create any newly earned ones.
    Idempotent: safe to call multiple times.
    """
    stats = get_user_stats(user)

    already_have = set(
        UserAchievement.objects.filter(user=user)
        .values_list("achievement__code", flat=True)
    )

    new_awards = []

    for achievement in Achievement.objects.all():
        if achievement.code in already_have:
            continue

        if is_eligible(achievement, stats):
            ua, created = UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement,
            )
            if created:
                new_awards.append(ua)

    return new_awards
