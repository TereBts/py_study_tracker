from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from goals.models import Goal, GoalOutcome
from study_sessions.models import StudySession

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

    context = {
        "active_goals_count": Goal.objects.filter(is_active=True).count(),
        "total_hours_this_week": total_hours,
        "recent_sessions": StudySession.objects.order_by('-started_at')[:5],
        "recent_outcomes": GoalOutcome.objects.order_by('-created_at')[:5],
        "week_start": week_start,
        "week_end": week_end - timedelta(days=1),  # inclusive display
    }
    return render(request, "tracker/dashboard.html", context)