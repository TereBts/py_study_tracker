from django.contrib import admin
from .models import Goal


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Goal model.

    Controls how user goals appear within the Django admin interface.
    This setup provides quick visibility into goal progress, related courses,
    and milestone information while allowing filtering and searching.

    list_display:
        - user: The owner of the goal.
        - course: The related course (if any).
        - weekly_hours_target: Weekly study hours target.
        - weekly_lessons_target: Weekly lesson completion target.
        - study_days_per_week: Planned number of study days per week.
        - total_required_lessons: Total lessons required to complete the goal.
        - milestone_name: Optional milestone or label for the goal.
        - milestone_date: Date associated with that milestone.
        - is_active: Whether the goal is currently active.
        - created_at: Timestamp when the goal was created.

    list_filter:
        Enables sidebar filters for quick narrowing of results by:
        - is_active status
        - milestone_date
        - course

    search_fields:
        Allows keyword searches by:
        - username of the goal’s owner
        - milestone name
        - course title
    """

    list_display = (
        "user",
        "course",
        "weekly_hours_target",
        "weekly_lessons_target",
        "study_days_per_week",
        "total_required_lessons",
        "milestone_name",
        "milestone_date",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "milestone_date", "course")
    search_fields = ("user__username", "milestone_name", "course__title")
