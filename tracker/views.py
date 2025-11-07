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
    today = timezone.localdate()                       # local date, e.g. Europe/London
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=7)             # next Monday (exclusive)

    # Sessions in current week (using started_at DateTimeField)
    weekly_sessions = StudySession.objects.filter(
        started_at__date__gte=week_start,
        started_at__date__lt=week_end,
    )

    total_minutes = weekly_sessions.aggregate(total=Sum('duration_minutes'))['total'] or 0
    total_hours = round(total_minutes / 60.0, 2)

    recent_achievements = (
        UserAchievement.objects.filter(user=user)
        .select_related("achievement")
        .order_by("-awarded_at")[:2]
    )

    stats = get_user_stats(user)

    next_hours_badge = (
        Achievement.objects.filter(rule_type="total_hours")
        .order_by("rule_params__threshold")
        .first()
    )

    next_hours_hint = None
    if next_hours_badge:
        threshold = next_hours_badge.rule_params.get("threshold", 0)
        current_hours = round(stats["total_minutes"] / 60, 1)
        remaining = max(threshold - current_hours, 0)
        if remaining > 0:
            next_hours_hint = f"{remaining}h until “{next_hours_badge.title}”"

    context = {
        "active_goals_count": Goal.objects.filter(is_active=True).count(),
        "total_hours_this_week": total_hours,
        "recent_sessions": StudySession.objects.order_by('-started_at')[:5],
        "recent_outcomes": GoalOutcome.objects.order_by('-created_at')[:5],
        "week_start": week_start,
        "week_end": week_end - timedelta(days=1),  # inclusive display
        "recent_achievements": recent_achievements,
        "next_hours_hint": next_hours_hint,
    }
    
    return render(request, "tracker/dashboard.html", context)