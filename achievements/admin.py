from django.contrib import admin
from .models import Achievement, UserAchievement


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Achievement model.

    Defines how achievements are displayed and filtered
    within the Django admin interface.

    list_display:
        Shows key identifying fields in the list view:
        - code: Unique slug for the achievement.
        - title: Human-readable name.
        - rule_type: Type of rule that determines unlocking.
        - icon: Optional icon name used in the front end.

    list_filter:
        Enables filtering by rule_type for easier navigation.
    """

    list_display = ("code", "title", "rule_type", "icon")
    list_filter = ("rule_type",)


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserAchievement model.

    Displays which users have unlocked which achievements,
    along with the date/time they were awarded.

    list_display:
        - user: The user who earned the achievement.
        - achievement: The related achievement instance.
        - awarded_at: The timestamp when it was awarded.

    list_filter:
        Allows filtering by achievement type in the admin panel.
    """

    list_display = ("user", "achievement", "awarded_at")
    list_filter = ("achievement",)
