from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
from goals.models import Goal

# Create your models here.
class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="study_sessions")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="study_sessions")
    goal = models.ForeignKey(Goal, on_delete=models.SET_NULL, null=True, blank=True, related_name="study_sessions")
    started_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        hrs = self.duration_minutes / 60
        return f"{self.user.username} • {self.course} • {hrs:.2f}h on {self.started_at.date()}"