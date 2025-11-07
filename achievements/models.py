from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Achievement(models.Model):
    code = models.SlugField(unique=True)  # e.g. "hours_5", "streak_4_weeks"
    title = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=40, blank=True)  # e.g. "trophy", "star"
    rule_type = models.CharField(max_length=40)         # e.g. "total_hours", "weekly_streak", "goals_completed"
    rule_params = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "achievement")

    def __str__(self):
        return f"{self.user} - {self.achievement.code}"
