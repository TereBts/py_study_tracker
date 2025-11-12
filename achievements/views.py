from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Achievement, UserAchievement
from .services import get_user_stats


@login_required
def achievement_list(request):
    """
    Display a list of achievements for the currently logged-in user.

    The view separates achievements into two categories:
    - Earned achievements: already unlocked by the user.
    - Locked achievements: not yet earned, with a progress hint showing
    how close
      the user is to unlocking them.

    It gathers user study statistics via `get_user_stats` and uses that data
    to determine progress toward each achievement.

    Args:
        request (HttpRequest): The HTTP request object containing user session
        data.

    Returns:
        HttpResponse: Renders 'achievements/achievement_list.html' with a
        context
        dictionary containing:
            - 'earned': A list of (Achievement, UserAchievement) tuples for
            unlocked items.
            - 'locked': A list of (Achievement, str) tuples, each with a
            progress hint.
    """
    user = request.user
    stats = get_user_stats(user)

    user_achievements = (
        UserAchievement.objects.filter(user=user)
        .select_related("achievement")
    )

    # Create a dictionary mapping achievement codes to earned achievements
    earned_by_code = {
        ua.achievement.code: ua for ua in user_achievements
    }

    earned = []
    locked = []

    # Split achievements into earned and locked with progress information
    for ach in Achievement.objects.all():
        ua = earned_by_code.get(ach.code)
        if ua:
            earned.append((ach, ua))
        else:
            locked.append((ach, build_progress_hint(ach, stats)))

    context = {
        "earned": earned,
        "locked": locked,
    }
    return render(request, "achievements/achievement_list.html", context)


def build_progress_hint(achievement, stats):
    """
    Generate a user-friendly progress message for a locked achievement.

    This helper function calculates how far the user has progressed toward
    unlocking
    a given achievement, based on their current study statistics.

    It supports multiple rule types:
        - 'total_hours': compares user's total study hours to a threshold.
        - 'goals_completed': compares completed goals to a target number.
        - 'weekly_streak': compares the current weekly streak to a goal
        number of weeks.

    Args:
        achievement (Achievement): The achievement instance being evaluated.
        stats (dict): A dictionary of user study stats (e.g., total_minutes,
            completed_goals, weekly_streak_weeks).

    Returns:
        str: A readable message describing progress toward the achievement,
        or an empty string if the rule type is unrecognized.
    """
    p = achievement.rule_params or {}

    if achievement.rule_type == "total_hours":
        threshold = p.get("threshold", 0)
        current_hours = round(stats["total_minutes"] / 60, 1)
        remaining = max(threshold - current_hours, 0)
        return (
            f"Study {threshold} total hours "
            f"(you’re at {current_hours}h, {remaining}h to go)."
        )

    if achievement.rule_type == "goals_completed":
        threshold = p.get("threshold", 0)
        current = stats["completed_goals"]
        remaining = max(threshold - current, 0)
        return (
            f"Complete {threshold} goals "
            f"(you’ve completed {current}, {remaining} to go)."
        )

    if achievement.rule_type == "weekly_streak":
        needed = p.get("weeks", 0)
        current = stats["weekly_streak_weeks"]
        remaining = max(needed - current, 0)
        return (
            f"Maintain a {needed}-week streak "
            f"(you’re at {current} weeks, {remaining} to go)."
        )
    return ""
