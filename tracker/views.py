from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
import json
from goals.models import Goal, GoalOutcome
from study_sessions.models import StudySession
from achievements.models import UserAchievement, Achievement
from achievements.services import get_user_stats
import random


def home(request):
    # Public landing page (visible to everyone)
    return render(request, "tracker/home.html")


from django.db.models.functions import TruncMonth

@login_required
def dashboard(request):
    user = request.user

    # ---------- Weekly summary (for your stat card) ----------
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())      # Monday
    week_end = week_start + timedelta(days=7)                 # next Monday (exclusive)

    weekly_sessions = StudySession.objects.filter(
        user=user,
        started_at__date__gte=week_start,
        started_at__date__lt=week_end,
    )

    total_minutes = weekly_sessions.aggregate(total=Sum("duration_minutes"))["total"] or 0
    total_hours_this_week = round(total_minutes / 60.0, 2)

    # ---------- Recent sessions & outcomes ----------
    recent_sessions = (
        StudySession.objects
        .filter(user=user)
        .select_related("course", "goal")
        .order_by("-started_at")[:5]
    )

    recent_outcomes = (
        GoalOutcome.objects
        .filter(goal__user=user)
        .select_related("goal")
        .order_by("-created_at")[:5]
    )

    # ---------- Monthly trend per goal (last 12 months) ----------
    months_back = 12
    # anchor at first of this month
    this_month_start = today.replace(day=1)

    # Generate month starts oldest -> newest
    months = []
    current = this_month_start
    for _ in range(months_back):
        months.append(current)
        # go back one month safely
        if current.month == 1:
            current = current.replace(year=current.year - 1, month=12)
        else:
            current = current.replace(month=current.month - 1)
    months = list(reversed(months))  # oldest first

    # Aggregate hours per goal per month
    # NOTE: use goal_id, not goal__title (your Goal has no title field)
    outcomes = (
        GoalOutcome.objects
        .filter(goal__user=user)
        .annotate(month=TruncMonth("week_start"))
        .values("goal_id", "month")
        .annotate(total_hours=Sum("hours_completed"))
        .order_by("month")
    )

    # Map goal_id -> label using __str__ on Goal (or fallback)
    goal_ids = {o["goal_id"] for o in outcomes}
    goals = Goal.objects.filter(id__in=goal_ids)
    goal_labels = {g.id: str(g) for g in goals}

    # Build {goal_id: {month: hours}}
    data_by_goal = {}
    for o in outcomes:
        gid = o["goal_id"]
        m = o["month"]
        hrs = float(o["total_hours"] or 0)

        if gid not in data_by_goal:
            data_by_goal[gid] = {
                "label": goal_labels.get(gid, f"Goal {gid}"),
                "values": {}
            }
        data_by_goal[gid]["values"][m] = hrs

    month_labels = [m.strftime("%b %Y") for m in months]

    # Simple distinct-ish colour generator
    def random_colour():
        hue = random.randint(0, 360)
        return f"hsl({hue}, 70%, 55%)"

    datasets = []
    for entry in data_by_goal.values():
        values_map = entry["values"]
        series = [round(values_map.get(m, 0), 2) for m in months]
        colour = random_colour()
        datasets.append({
            "label": entry["label"],
            "data": series,
            "borderColor": colour,
            "backgroundColor": colour,
            "tension": 0.4,
            "borderWidth": 2,
            "fill": False,
            "pointRadius": 3,
        })

    monthly_labels_json = json.dumps(month_labels)
    monthly_datasets_json = json.dumps(datasets)

    # ---------- Achievements strip (unchanged logic) ----------
    recent_achievements = (
        UserAchievement.objects
        .filter(user=user)
        .select_related("achievement")
        .order_by("-awarded_at")[:2]
    )

    stats = get_user_stats(user)
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
        "active_goals_count": Goal.objects.filter(user=user, is_active=True).count()
        if hasattr(Goal, "is_active")
        else Goal.objects.filter(user=user).count(),

        "total_hours_this_week": total_hours_this_week,
        "recent_sessions": recent_sessions,
        "recent_outcomes": recent_outcomes,
        "week_start": week_start,
        "week_end": week_end - timedelta(days=1),

        "recent_achievements": recent_achievements,
        "next_hours_hint": next_hours_hint,

        # Chart data
        "monthly_labels_json": monthly_labels_json,
        "monthly_datasets_json": monthly_datasets_json,
    }

    return render(request, "tracker/dashboard.html", context)