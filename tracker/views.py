from django.shortcuts import render
from django.http import HttpResponse
from goals.models import Goal, GoalOutcome
from study_sessions.models import StudySession
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum

# Create your views here.
def dashboard(request):
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=7)
    weekly_sessions = StudySession.objects.filter(date__gte=week_start, date__lt=week_end)
    total_minutes = weekly_sessions.aggregate(total=Sum('duration_minutes'))['total'] or 0
    total_hours = round(total_minutes / 60, 2)
    active_goals = Goal.objects.filter(is_active=True).count()
    recent_sessions = StudySession.objects.order_by('-date')[:5]
    recent_outcomes = GoalOutcome.objects.order_by('-created_at')[:5]

    context = {
        'active_goals_count': active_goals,
        'total_hours_this_week': total_hours,
        'recent_sessions': recent_sessions,
        'recent_outcomes': recent_outcomes,
        'week_start': week_start,
        'week_end': week_end - timedelta(days=1),
    }
return render(request, "tracker/dashboard.html", context)
