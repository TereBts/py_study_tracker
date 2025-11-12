from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
from goals.models import Goal


class StudySession(models.Model):
    """
    Represents a single logged study session by a user.

    Each session records which course was studied, its duration in minutes,
    an optional linked goal, and any notes the user entered. These records
    are used to calculate weekly and overall progress across courses and goals.

    Attributes:
        user (User): The user who logged the study session.
        course (Course): The course this session relates to.
        goal (Goal | None): Optional related goal. Null if not tied to a goal.
        started_at (datetime): The date and time the session began.
        duration_minutes (int): Length of the session in minutes.
        notes (str): Optional notes about the study session.

    Meta:
        ordering (list): Sessions are ordered by most recent start time.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="study_sessions",
        help_text="The user who logged this study session.",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="study_sessions",
        help_text="The course this study session is linked to.",
    )
    goal = models.ForeignKey(
        Goal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="study_sessions",
        help_text="Optional goal this session contributes to.",
    )
    started_at = models.DateTimeField(
        help_text="Date and time the study session started."
    )
    duration_minutes = models.PositiveIntegerField(
        help_text="Duration of the study session in minutes."
    )
    notes = models.TextField(
        blank=True,
        help_text="Optional notes or reflections about the session."
        )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        """
        Return a readable summary of the study session.

        Returns:
            str: Formatted string showing username, course, duration in hours,
            and date.
        """
        hrs = self.duration_minutes / 60
        return (
            f"{self.user.username} • {self.course} • "
            f"{hrs:.2f}h on {self.started_at.date()}"
        )
