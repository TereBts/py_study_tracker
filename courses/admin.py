from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Course model.

    Controls how course records are displayed, searched, and filtered
    within the Django admin interface. Provides quick visibility into
    course ownership, progress status, and scheduling information.

    list_display:
        - title: The name of the course.
        - owner: The user who created or owns the course.
        - status: The current state of the course (e.g., active, completed).
        - start_date / end_date: Timeframe for the course.
        - created_at: Timestamp when the course entry was added.

    list_filter:
        Enables sidebar filtering options for status and creation date.

    search_fields:
        Allows text-based search by course title, provider, or owner information
        (via email or username).

    autocomplete_fields:
        Replaces the standard dropdown for 'owner' with an autocomplete input,
        useful for databases with many users.
    """

    list_display = ("title", "owner", "status", "start_date", "end_date", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "provider", "owner__email", "owner__username")
    autocomplete_fields = ("owner",)