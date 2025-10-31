from django.contrib import admin
from .models import Goal

# Register your models here.
@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "weekly_hours_target", "weekly_lessons_target",
                    "study_days_per_week", "total_required_lessons", "milestone_name",
                    "milestone_date", "is_active", "created_at")
    list_filter = ("is_active", "milestone_date", "course")
    search_fields = ("user__username", "milestone_name", "course__title")