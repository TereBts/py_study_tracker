from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Achievement(models.Model):
    """
    Represents an achievement or milestone that users can unlock
    within the StudyStar platform.

    Each achievement has a unique code (e.g. "hours_5", "streak_4_weeks"),
    a display title and description, an optional icon identifier, and
    rule data defining the conditions under which it is awarded.

    Fields:
        code (SlugField): Unique slug identifier for the achievement.
        title (CharField): Human-readable name for the achievement.
        description (TextField): Optional description explaining what
          the achievement means.
        icon (CharField): Optional icon name (e.g. "trophy", "star") for
          frontend display.
        rule_type (CharField): The logical rule type that determines how
        it is awarded
            (e.g. "total_hours", "weekly_streak", "goals_completed").
        rule_params (JSONField): A JSON object with additional parameters
            used by rule evaluation logic.
    """

    code = models.SlugField(unique=True)
    title = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    rule_type = models.CharField(max_length=40)
    rule_params = models.JSONField(default=dict, blank=True)

    def __str__(self):
        """
        Returns a string representation of the achievement,
        typically its title for use in admin and templates.
        """
        return self.title


class UserAchievement(models.Model):
    """
    Links a user to an achievement they have unlocked.

    This model records which achievements have been earned by each user,
    along with the timestamp when it was awarded. Each (user, achievement)
    pair is unique to prevent duplicate awards.

    Fields:
        user (ForeignKey): The user who earned the achievement.
        achievement (ForeignKey): The related achievement instance.
        awarded_at (DateTimeField): The date and time when the achievement
        was unlocked.

    Meta:
        unique_together: Ensures a user cannot earn the same achievement more
        than once.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "achievement")

    def __str__(self):
        """
        Returns a string combining the username and the achievement code,
        useful for admin display and debugging.
        """
        return f"{self.user} - {self.achievement.code}"
