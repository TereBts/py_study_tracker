from datetime import timedelta, date

from django.utils import timezone
from django.db.models import Sum, Count, Q

from .models import Achievement, UserAchievement
from study_sessions.models import StudySession   
from goals.models import GoalOutcome            


def get_user_stats(user):
    # total minutes
    total_minutes = StudySession.objects.filter(user=user).aggregate(
        total=Sum('duration_minutes')  # or calculate from start/end if needed
    )['total'] or 0

    # goals completed count
    # adjust field names according to your GoalOutcome implementation
    completed_goals = GoalOutcome.objects.filter(
        user=user,
        status='completed'  # or whatever you use to mark completion
    ).count()

    # build a weekly streak: count consecutive weeks (from current week backwards)
    # where user has at least one session in that ISO week
    sessions = StudySession.objects.filter(user=user).values_list('start_time', flat=True)
    weeks_with_study = set()
    for s in sessions:
        dt = s.date() if isinstance(s, date) else s.date()
        year, week, _ = dt.isocalendar()
        weeks_with_study.add((year, week))

    if weeks_with_study:
        today = timezone.localdate()
        year, week, _ = today.isocalendar()
        streak = 0
        while (year, week) in weeks_with_study:
            streak += 1
            # go to previous week
            week -= 1
            if week == 0:
                year -= 1
                week = date(year, 12, 28).isocalendar()[1]
    else:
        streak = 0

    return {
        "total_minutes": total_minutes,
        "completed_goals": completed_goals,
        "weekly_streak_weeks": streak,
    }


def evaluate_achievements_for_user(user):
    """Return list of newly awarded UserAchievement objects."""
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


def is_eligible(achievement, stats):
    """Decide if the user matches this achievement based on rule_type & params."""
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

    return False
