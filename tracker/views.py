"""Public and authenticated views for the StudyStar tracker app.

Includes:
- Public pages: home, about, contact
- Authenticated dashboard summarising weekly activity, recent
sessions/outcomes,
  monthly trend data for charts, and an achievements strip.
"""

from django.shortcuts import render, redirect
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
from django.contrib import messages
from django.db.models.functions import TruncMonth
from .models import ContactMessage



def home(request):
    """
    Public landing page.

    If the user is authenticated, redirect straight to the dashboard;
    otherwise, render the marketing/landing template.

    Args:
        request (HttpRequest): The incoming request.

    Returns:
        HttpResponse | HttpResponseRedirect: Rendered home page or redirect.
    """
    if request.user.is_authenticated:
        return redirect("tracker:dashboard")
    return render(request, "tracker/home.html")


def about(request):
    """
    Render the public About page.

    Returns:
        HttpResponse: The rendered about template.
    """
    return render(request, "tracker/about.html")


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage


def contact(request):
    """
    Render and process the public Contact form.

    On POST:
        - Validates presence of name, email, and message.
        - Saves the message to the database, including the user (if logged in).
        - Shows a success or error message.
    """
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if name and email and message:
            ContactMessage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                message=message,
            )

            messages.success(
                request,
                "Thanks for getting in touch. We’ll get back to you as soon as possible.",
            )
            return redirect("tracker:contact")

        else:
            messages.error(
                request, "Please fill in all fields before submitting."
            )

    return render(request, "tracker/contact.html")


@login_required
def dashboard(request):
    """
    Authenticated dashboard summarising a user's recent study activity.

    Sections:
        - Weekly summary card: total hours this week (Mon–Sun).
        - Recent sessions (up to 5) with course/goal info.
        - Recent frozen GoalOutcome snapshots (up to 5).
        - Monthly trend (last 12 months): aggregated hours per goal for
        Chart.js.
        - Achievements strip: two most recent + next hours milestone hint.

    Context:
        active_goals_count (int): Count of active goals (fallback to all if no
        flag).
        total_hours_this_week (float): Hours studied this week, rounded to 2
        dp.
        recent_sessions (QuerySet[StudySession]): Latest 5 sessions.
        recent_outcomes (QuerySet[GoalOutcome]): Latest 5 outcomes.
        week_start (date): Monday of the current ISO week.
        week_end (date): Sunday of the current ISO week.
        recent_achievements (QuerySet[UserAchievement]): Latest 2 awards.
        next_hours_hint (str | None): e.g., '3.5h until “Bronze Hours”'.
        monthly_labels_json (str): JSON array of month labels for chart.
        monthly_datasets_json (str): JSON array of dataset configs for chart.

    Returns:
        HttpResponse: Rendered dashboard template.
    """
    user = request.user

    # ---------- Weekly summary ----------
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=7)  # next Monday

    weekly_sessions = StudySession.objects.filter(
        user=user,
        started_at__date__gte=week_start,
        started_at__date__lt=week_end,
    )
    total_minutes = (
        weekly_sessions.aggregate(total=Sum("duration_minutes"))["total"]
        or 0
    )
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
    this_month_start = today.replace(day=1)

    # Generate month starts oldest -> newest
    months = []
    current = this_month_start
    for _ in range(months_back):
        months.append(current)
        if current.month == 1:
            current = current.replace(year=current.year - 1, month=12)
        else:
            current = current.replace(month=current.month - 1)
    months = list(reversed(months))  # oldest first

    outcomes = (
        GoalOutcome.objects
        .filter(goal__user=user)
        .annotate(month=TruncMonth("week_start"))
        .values("goal_id", "month")
        .annotate(total_hours=Sum("hours_completed"))
        .order_by("month")
    )

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

    def random_colour():
        """Return a distinct-ish HSL colour string for chart lines."""
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

    # ---------- Achievements strip ----------
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
        "active_goals_count": (
            Goal.objects.filter(user=user, is_active=True).count()
            if hasattr(Goal, "is_active")
            else Goal.objects.filter(user=user).count()
        ),

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
