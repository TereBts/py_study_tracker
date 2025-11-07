from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Achievement, UserAchievement
from .services import get_user_stats


@login_required
def achievement_list(request):
    user = request.user
    stats = get_user_stats(user)

    user_achievements = (
        UserAchievement.objects.filter(user=user)
        .select_related("achievement")
    )

    earned_by_code = {
        ua.achievement.code: ua for ua in user_achievements
    }

    earned = []
    locked = []

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
    p = achievement.rule_params or {}

    if achievement.rule_type == "total_hours":
        threshold = p.get("threshold", 0)
        current_hours = round(stats["total_minutes"] / 60, 1)
        remaining = max(threshold - current_hours, 0)
        return f"Study {threshold} total hours (you’re at {current_hours}h, {remaining}h to go)."

    if achievement.rule_type == "goals_completed":
        threshold = p.get("threshold", 0)
        current = stats["completed_goals"]
        remaining = max(threshold - current, 0)
        return f"Complete {threshold} goals (you’ve completed {current}, {remaining} to go)."

    if achievement.rule_type == "weekly_streak":
        needed = p.get("weeks", 0)
        current = stats["weekly_streak_weeks"]
        remaining = max(needed - current, 0)
        return f"Maintain a {needed}-week streak (you’re at {current} weeks, {remaining} to go)."

    return ""
