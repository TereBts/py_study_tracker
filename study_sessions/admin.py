from django.contrib import admin
from .models import StudySession


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the StudySession model.

    Defines how study sessions are displayed, filtered, and searched
    within the Django admin interface. Provides quick visibility into
    who studied what, when, and for how long.

    list_display:
        - user: The user who logged the study session.
        - course: The course associated with the session.
        - goal: The goal linked to this study session (if any).
        - started_at: The date/time the session began.
        - duration_minutes: Total duration of the session in minutes.

    list_filter:
        Enables sidebar filtering by course, goal, and start date.

    search_fields:
        Allows text-based search by username, course title, or notes.

    autocomplete_fields:
        Enables autocomplete inputs for foreign keys to improve usability
        in large datasets (user, course, goal).
    """

    list_display = ("user", "course", "goal", "started_at", "duration_minutes")
    list_filter = ("course", "goal", "started_at")
    search_fields = ("user__username", "course__title", "notes")
    autocomplete_fields = ("user", "course", "goal")
