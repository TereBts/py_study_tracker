from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q, CheckConstraint
from courses.models import Course
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from datetime import timedelta

# Create your models here.
def validate_half_hours(value):
    q = (Decimal(value) * 2) % 1
    if q != 0:
        raise ValidationError("Hours must be in 0.5 increments (e.g., 1, 1.5, 2).")

class Goal(models.Model):
    """
    A user’s study goal for a course or for general study.
    Supports weekly pacing (hours and/or lessons) and long-term milestones.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals")
    # Tie to a specific course the user is taking:
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="goals", null=True, blank=True
    ) 
    # Weekly pacing targets (either can be set, both allowed):
    weekly_hours_target = models.DecimalField(
        max_digits=5,
        decimal_places=1,  # one decimal place (e.g., 1.5)
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.0")), validate_half_hours],
        help_text="Target study hours per week in 0.5 steps."
    )
    weekly_lessons_target = models.PositiveIntegerField(
        null=True, blank=True, help_text="How many lessons/modules do you aim to complete per week?"
    )
    # How many days per week they plan to study (used to derive daily targets):
    study_days_per_week = models.PositiveSmallIntegerField(
        default=5, help_text="How many days per week will you study? (1–7)."
    )
    # Milestone / long-term target:
    total_required_lessons = models.PositiveIntegerField(
        null=True, blank=True, help_text="How many lessons/modules need to be completed for the milestone?"
    )
    milestone_name = models.CharField(
        max_length=120, null=True, blank=True, help_text="e.g., 'Assignment 2' or 'Course completion'"
    )
    milestone_date = models.DateField(null=True, blank=True, help_text="Deadline for the milestone.")
    # Optional: if you want to derive hours pace from a lessons goal:
    avg_hours_per_lesson = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="If set, we can estimate hours needed from lesson targets."
    )
    # Lifecycle:
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# ---- Validation ----
    def clean(self):
        super().clean()

        if self.weekly_hours_target is None and self.weekly_lessons_target is None and self.total_required_lessons is None:
            raise ValidationError(
                "Provide at least a weekly hours target, a weekly lessons target, or a milestone total."
            )

        if self.study_days_per_week < 1 or self.study_days_per_week > 7:
            raise ValidationError("Study days per week must be between 1 and 7.")

        # If a milestone date is set, it should be in the future
        if self.milestone_date and self.milestone_date < timezone.localdate():
            raise ValidationError("Milestone date must be today or in the future.")

        # If no weekly lessons target but you want hours from lessons, you can still set avg_hours_per_lesson
        # We only guard nonsensical values here.
        if self.avg_hours_per_lesson is not None and self.avg_hours_per_lesson <= 0:
            raise ValidationError("Average hours per lesson must be positive if provided.")

        # If you set total_required_lessons, it should be > 0
        if self.total_required_lessons is not None and self.total_required_lessons == 0:
            raise ValidationError("Total required lessons must be greater than zero.")

# ---- Derived targets for UI display ----
    @property
    def daily_hours_target(self):
        """If weekly hours target is set, divide by study days."""
        if self.weekly_hours_target is None:
            return None
        return float(self.weekly_hours_target) / self.study_days_per_week

    @property
    def daily_lessons_target(self):
        """If weekly lessons target is set, divide by study days."""
        if self.weekly_lessons_target is None:
            return None
        return self.weekly_lessons_target / self.study_days_per_week

    # ---- Milestone pacing helpers ----
    def weeks_until_milestone(self, today=None):
        """Whole/fractional weeks left until the deadline (>= 0)."""
        if not self.milestone_date:
            return None
        today = today or timezone.localdate()
        days = (self.milestone_date - today).days
        return max(0, days / 7)

    def lessons_per_week_to_hit_milestone(self, lessons_completed=0, today=None):
        """
        If total_required_lessons + milestone_date are set, compute the lessons/week
        needed from 'today' to the milestone.
        """
        if not self.total_required_lessons or not self.milestone_date:
            return None

        remaining = max(0, self.total_required_lessons - int(lessons_completed))
        weeks = self.weeks_until_milestone(today=today)

        if weeks is None or weeks == 0:
            # If the deadline is today or passed, we either return remaining (do all now) or None
            return float("inf") if remaining > 0 else 0

        return remaining / weeks

    def hours_per_week_to_hit_milestone(self, lessons_completed=0, today=None):
        """
        If avg_hours_per_lesson is known, derive hours/week needed for milestone.
        """
        if self.avg_hours_per_lesson is None:
            return None

        lpw = self.lessons_per_week_to_hit_milestone(lessons_completed=lessons_completed, today=today)
        if lpw in (None, float("inf")):
            return lpw

        return float(self.avg_hours_per_lesson) * lpw

    def daily_requirements_from_milestone(self, lessons_completed=0, today=None):
        """
        Turn milestone pacing into daily numbers based on study_days_per_week.
        Returns (daily_lessons, daily_hours or None).
        """
        lpw = self.lessons_per_week_to_hit_milestone(lessons_completed=lessons_completed, today=today)
        if lpw is None:
            return None, None

        daily_lessons = float("inf") if lpw == float("inf") else lpw / self.study_days_per_week

        hpw = self.hours_per_week_to_hit_milestone(lessons_completed=lessons_completed, today=today)
        daily_hours = None
        if hpw is not None:
            daily_hours = float("inf") if hpw == float("inf") else hpw / self.study_days_per_week

        return daily_lessons, daily_hours

    # ---- Progress aggregation from logged study sessions ----
    def total_study_minutes(self):
        """
        Sum of all minutes from StudySession rows linked to this goal (lifetime).
        Assumes StudySession has fields: goal (FK to Goal) and duration_minutes (int).
        """
        from study_sessions.models import StudySession
        agg = StudySession.objects.filter(goal=self).aggregate(total=Sum("duration_minutes"))
        return agg["total"] or 0

    def total_study_hours(self, decimals=1):
        """Lifetime total hours, derived from minutes, rounded for display."""
        return round(self.total_study_minutes() / 60, decimals)

    def weekly_study_minutes(self, today=None):
        """
        Minutes logged for this goal in the current ISO week (Mon–Sun).
        Uses started_at__date filter to avoid timezone gotchas.
        """
        from study_sessions.models import StudySession
        today = today or timezone.localdate()
        week_start = today - timedelta(days=today.weekday())          # Monday
        week_end = week_start + timedelta(days=7)                      # next Monday (exclusive)

        agg = (
            StudySession.objects
            .filter(
                goal=self,
                started_at__date__gte=week_start,
                started_at__date__lt=week_end,
            )
            .aggregate(total=Sum("duration_minutes"))
        )
        return agg["total"] or 0

    def weekly_progress_percent(self, today=None):
        """
        % progress against weekly_hours_target based on minutes logged this week.
        Returns None if no weekly target is set.
        """
        if self.weekly_hours_target is None:
            return None
        target_minutes = float(self.weekly_hours_target) * 60
        if target_minutes <= 0:
            return 0
        done = self.weekly_study_minutes(today=today)
        return min(100, round((done / target_minutes) * 100))

    def projected_completion_date(self):
        """
        Estimate a completion date based on current pace.
        Returns a date or None if not enough data yet.
        """
        from study_sessions.models import StudySession  # import here to avoid circulars

        total_required = self.total_required_minutes()
        if not total_required or total_required <= 0:
            return None

        done = self.total_study_minutes()
        if done == 0:
            return None

        # Get sessions for THIS goal (don’t rely on reverse name)
        qs = StudySession.objects.filter(goal=self, started_at__isnull=False).order_by("started_at")
        first = qs.first()
        if not first:
            return None

        now = timezone.now()
        days_elapsed = (now - first.started_at).days or 1
        weeks_elapsed = days_elapsed / 7

        total_hours_done = done / 60
        pace_h_per_week = total_hours_done / weeks_elapsed if weeks_elapsed > 0 else None
        if not pace_h_per_week or pace_h_per_week <= 0:
            return None

        total_required_hours = total_required / 60
        hours_remaining = max(0, total_required_hours - total_hours_done)
        weeks_remaining = hours_remaining / pace_h_per_week

        return (now + timedelta(weeks=weeks_remaining)).date()
    
        # ---- Overall requirement & progress (hours-based) ----
    def total_required_minutes(self):
        """
        Estimate total minutes needed to finish this goal.
        Preferred: avg_hours_per_lesson * total_required_lessons.
        Returns an int minutes, or None if not enough info is set.
        """
        if self.avg_hours_per_lesson and self.total_required_lessons:
            return int(float(self.avg_hours_per_lesson) * int(self.total_required_lessons) * 60)
        # Optional fallback could use weekly target + milestone_date, but we keep it strict for accuracy.
        return None

    def total_required_hours(self, decimals=1):
        """Estimated total hours needed, rounded for display, or None if unknown."""
        minutes = self.total_required_minutes()
        if not minutes:
            return None
        return round(minutes / 60, decimals)

    def overall_progress_percent(self):
        """
        % of the estimated total minutes completed (lifetime).
        Returns None if total_required_minutes is unavailable.
        """
        required = self.total_required_minutes()
        if not required or required <= 0:
            return None
        done = self.total_study_minutes()
        return min(100, round((done / required) * 100))

    # ---- Convenience: weekly hours (for templates) ----
    def weekly_study_hours(self, decimals=1):
        """This week's logged time in hours, rounded for display."""
        return round(self.weekly_study_minutes() / 60, decimals)

    # ---- Projection based on current pace ----
    def projected_completion_date(self):
        """
        Estimate a completion date based on current pace (hours/week).
        Returns a date, or None if not enough data yet.
        """
        from study_sessions.models import StudySession  # local import to avoid circulars

        total_required = self.total_required_minutes()
        if not total_required or total_required <= 0:
            return None

        done_minutes = self.total_study_minutes()
        if done_minutes == 0:
            return None

        qs = StudySession.objects.filter(goal=self, started_at__isnull=False).order_by("started_at")
        first = qs.first()
        if not first:
            return None

        now = timezone.now()
        days_elapsed = (now - first.started_at).days or 1
        weeks_elapsed = days_elapsed / 7

        total_hours_done = done_minutes / 60
        pace_h_per_week = total_hours_done / weeks_elapsed if weeks_elapsed > 0 else None
        if not pace_h_per_week or pace_h_per_week <= 0:
            return None

        total_required_hours = total_required / 60
        hours_remaining = max(0, total_required_hours - total_hours_done)
        weeks_remaining = hours_remaining / pace_h_per_week

        return (now + timedelta(weeks=weeks_remaining)).date()

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
    
class GoalOutcome(models.Model):
    """
    Weekly frozen snapshot of a user's goal progress.
    week_start is the Monday of the ISO week.
    """
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="outcomes")
    week_start = models.DateField()
    week_end = models.DateField()
    hours_completed = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    hours_target = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    lessons_target = models.PositiveIntegerField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["goal", "week_start"], name="unique_goal_week")
        ]
        ordering = ["-week_start"]

    def __str__(self):
        name = (
            self.goal.course.title
            if self.goal.course
            else self.goal.milestone_name
            or "General goal"
        )
        return f"{name} — {self.week_start} ({'✓' if self.completed else '✗'})"

