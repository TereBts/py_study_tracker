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
    # Private page (login required)
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=7)

    weekly_sessions = StudySession.objects.filter(date__gte=week_start, date__lt=week_end)
    total_minutes = weekly_sessions.aggregate(total=Sum('duration_minutes'))['total'] or 0
    context = {
        "active_goals_count": Goal.objects.filter(is_active=True).count(),
        "total_hours_this_week": round(total_minutes / 60, 2),
        "recent_sessions": StudySession.objects.order_by('-date')[:5],
        "recent_outcomes": GoalOutcome.objects.order_by('-created_at')[:5],
        "week_start": week_start,
        "week_end": week_end - timedelta(days=1),
    }
    return render(request, "tracker/dashboard.html", context)
