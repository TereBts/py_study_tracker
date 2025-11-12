from datetime import date
from django.utils import timezone
from django.db.models import Sum

from .models import Achievement, UserAchievement
from study_sessions.models import StudySession
from goals.models import GoalOutcome


def get_user_stats(user):
    """
    Collect study-related statistics for a given user.

    This function aggregates key performance metrics used to evaluate
    achievement progress, including total study time, number of completed
    goals,
    and the user’s current weekly streak.

    Logic overview:
        - Total minutes are summed across all StudySession records.
        - Completed goals are counted via GoalOutcome entries marked as
        completed.
        - Weekly streak counts consecutive ISO weeks (ending with the current
        week)
          in which the user has logged at least one study session.

    Args:
        user (User): The user instance whose stats are being calculated.

    Returns:
        dict: A dictionary with the following keys:
            - "total_minutes" (int): Total study minutes logged.
            - "completed_goals" (int): Number of completed goals.
            - "weekly_streak_weeks" (int): Number of consecutive
            active study weeks.
    """
    # Total study minutes for this user
    total_minutes = (
        StudySession.objects.filter(user=user)
        .aggregate(total=Sum("duration_minutes"))
        .get("total") or 0
    )

    # Count of completed goals owned by this user
    completed_goals = GoalOutcome.objects.filter(
        goal__user=user,
        completed=True
    ).count()

    # Determine weekly streak: consecutive ISO weeks
    # with at least one study session
    sessions = (
        StudySession.objects
        .filter(user=user)
        .values_list("started_at", flat=True)
    )

    weeks_with_study = set()
    for dt in sessions:
        d = dt.date()
        year, week, _ = d.isocalendar()
        weeks_with_study.add((year, week))

    streak = 0
    if weeks_with_study:
        today = timezone.localdate()
        year, week, _ = today.isocalendar()

        # Walk backwards through weeks while activity continues
        while (year, week) in weeks_with_study:
            streak += 1
            week -= 1
            if week == 0:
                year -= 1
                # Handle ISO week rollover at new year
                week = date(year, 12, 28).isocalendar()[1]

    return {
        "total_minutes": total_minutes,
        "completed_goals": completed_goals,
        "weekly_streak_weeks": streak,
    }


def is_eligible(achievement, stats):
    """
    Determine if a user qualifies for a specific achievement.

    Compares the user’s statistics (from `get_user_stats`) to the
    achievement’s rule type and parameters to see if they meet
    the conditions required to unlock it.

    Supported rule types:
        - "total_hours": unlocks after total study hours >= threshold.
        - "goals_completed": unlocks after completed goals >= threshold.
        - "weekly_streak": unlocks after maintaining a streak >= weeks target.

    Args:
        achievement (Achievement): The achievement to evaluate.
        stats (dict): A dictionary of user statistics from `get_user_stats()`.

    Returns:
        bool: True if the user meets or exceeds the achievement criteria,
        False otherwise.
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

    # Unknown or unsupported rule types default to False
    return False


def evaluate_achievements_for_user(user):
    """
    Evaluate all achievements for a user and award any newly earned ones.

    This function checks every Achievement in the system and determines
    whether the given user qualifies for it based on their current stats.
    Any newly earned achievements are recorded in UserAchievement.

    The function is **idempotent** — calling it multiple times will not
    create duplicate entries for the same achievement.

    Args:
        user (User): The user whose achievements are being evaluated.

    Returns:
        list[UserAchievement]: A list of newly created UserAchievement
        instances
        (empty if the user earned none this round).
    """
    stats = get_user_stats(user)

    # Get all achievement codes the user already owns
    already_have = set(
        UserAchievement.objects.filter(user=user)
        .values_list("achievement__code", flat=True)
    )

    new_awards = []

    # Check each achievement and create new ones if eligible
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
