from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q, CheckConstraint
from courses.models import Course

# Create your models here.
class Goal(models.Model):
    """
    A user’s study goal for a course or for general study.
    Supports weekly pacing (hours and/or lessons) and long-term milestones.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals")
    # Tie to a specific course the user is taking
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="goals", null=True, blank=True
    )

    # Weekly pacing targets (either can be set, both allowed)
    weekly_hours_target = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="Target study hours per week."
    )
    weekly_lessons_target = models.PositiveIntegerField(
        null=True, blank=True, help_text="How many lessons/modules do you aim to complete per week?"
    )

    # How many days per week they plan to study (used to derive daily targets)
    study_days_per_week = models.PositiveSmallIntegerField(
        default=5, help_text="How many days per week will you study? (1–7)."
    )

    # Milestone / long-term target
    total_required_lessons = models.PositiveIntegerField(
        null=True, blank=True, help_text="How many lessons/modules need to be completed for the milestone?"
    )
    milestone_name = models.CharField(
        max_length=120, null=True, blank=True, help_text="e.g., 'Assignment 2' or 'Course completion'"
    )
    milestone_date = models.DateField(null=True, blank=True, help_text="Deadline for the milestone.")

    # Optional: if you want to derive hours pace from a lessons goal
    avg_hours_per_lesson = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="If set, we can estimate hours needed from lesson targets."
    )

    # Lifecycle
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_active", "-created_at"]
        constraints = [
            # study_days_per_week must be between 1 and 7
            CheckConstraint(check=Q(study_days_per_week__gte=1) & Q(study_days_per_week__lte=7),
                            name="goals_days_between_1_and_7"),
            # At least one of weekly targets OR a milestone target must be provided
            CheckConstraint(
                check=(
                    Q(weekly_hours_target__isnull=False) |
                    Q(weekly_lessons_target__isnull=False) |
                    Q(total_required_lessons__isnull=False)
                ),
                name="goals_need_some_target"
            ),
        ]

    def __str__(self):
        base = f"{self.user} Goal"
        if self.course:
            base += f" · {self.course.title}"
        if self.milestone_name:
            base += f" · {self.milestone_name}"
        return base




