from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum

from goals.models import Goal, GoalOutcome
from study_sessions.models import StudySession
from achievements.models import UserAchievement, Achievement
from achievements.services import get_user_stats


def home(request):
    # Public landing page (visible to everyone)
    return render(request, "tracker/home.html")


@login_required
def dashboard(request):
    user = request.user  # ✅ define user

    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())   # Monday
    week_end = week_start + timedelta(days=7)              # next Monday (exclusive)

    # ✅ Sessions in current week for this user
    weekly_sessions = StudySession.objects.filter(
        user=user,
        started_at__date__gte=week_start,
        started_at__date__lt=week_end,
    )

    total_minutes = weekly_sessions.aggregate(total=Sum("duration_minutes"))["total"] or 0
    total_hours = round(total_minutes / 60.0, 2)

    # ✅ Recent achievements (for this user)
    recent_achievements = (
        UserAchievement.objects
        .filter(user=user)
        .select_related("achievement")
        .order_by("-awarded_at")[:2]
    )

    # ✅ Stats for progress hint
    stats = get_user_stats(user)

    # Find the next unearned total_hours achievement in order of threshold
    earned_codes = set(
        UserAchievement.objects
        .filter(user=user)
        .values_list("achievement__code", flat=True)
    )

    total_hours_achs = (
        Achievement.objects
        .filter(rule_type="total_hours")
        .order_by("rule_params__threshold")
    )

    next_hours_hint = None
    current_hours = round(stats["total_minutes"] / 60, 1)

    for ach in total_hours_achs:
        if ach.code not in earned_codes:
            threshold = ach.rule_params.get("threshold", 0)
            remaining = max(threshold - current_hours, 0)
            if remaining > 0:
                next_hours_hint = f"{remaining}h until “{ach.title}”"
            break

    context = {
        # only this user's active goals
        "active_goals_count": Goal.objects.filter(user=user, is_active=True).count()
        if hasattr(Goal, "is_active")
        else Goal.objects.filter(user=user).count(),

        "total_hours_this_week": total_hours,

        # recent sessions + outcomes for this user
        "recent_sessions": (
            StudySession.objects
            .filter(user=user)
            .select_related("course", "goal")
            .order_by("-started_at")[:5]
        ),
        "recent_outcomes": (
            GoalOutcome.objects
            .filter(goal__user=user)
            .order_by("-created_at")[:5]
        ),

        "week_start": week_start,
        "week_end": week_end - timedelta(days=1),  # inclusive display

        "recent_achievements": recent_achievements,
        "next_hours_hint": next_hours_hint,
    }

    return render(request, "tracker/dashboard.html", context)
