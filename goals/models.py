from django.db import models
from django.db.models import Sum, Q, CheckConstraint
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from django.core.validators import MinValueValidator
from datetime import timedelta


def validate_half_hours(value):
    """
    Validate that a decimal hour value is in 0.5 increments.

    Args:
        value (Decimal): The numeric value to validate.

    Raises:
        ValidationError: If the value is not divisible by 0.5.
    """
    q = (Decimal(value) * 2) % 1
    if q != 0:
        raise ValidationError(
            "Hours must be in 0.5 increments (e.g., 1, 1.5, 2)."
            )


class Goal(models.Model):
    """
    Represents a user’s study goal for a course or independent study.

    A Goal supports weekly pacing (hours and/or lessons), optional
    long-term milestones, and progress tracking over time.

    Attributes:
        user (User): The owner of this goal.
        course (Course): Optional related course.
        weekly_hours_target (Decimal): Weekly study hour target.
        weekly_lessons_target (int): Weekly lesson completion target.
        study_days_per_week (int): Number of study days planned per week (1–7).
        total_required_lessons (int): Total lessons required to reach the
        milestone.
        milestone_name (str): Label for the milestone (e.g., "Assignment 2").
        milestone_date (date): Optional target completion date.
        avg_hours_per_lesson (Decimal): Optional conversion factor for
        hours/lesson.
        is_active (bool): Whether the goal is active.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last modification timestamp.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="goals",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="goals",
        null=True,
        blank=True,
    )
    weekly_hours_target = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.0")), validate_half_hours],
        help_text="Target study hours per week in 0.5 steps.",
    )
    weekly_lessons_target = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="How many lessons/modules do you aim to complete per week?",
    )
    study_days_per_week = models.PositiveSmallIntegerField(
        default=5,
        help_text="How many days per week will you study? (1–7).",
    )
    total_required_lessons = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="How many lessons/modules need to be completed for the"
        "milestone?",
    )
    milestone_name = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        help_text="e.g., 'Assignment 2' or 'Course completion'",
    )
    milestone_date = models.DateField(
        null=True, blank=True, help_text="Deadline for the milestone."
    )
    avg_hours_per_lesson = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="If set, we can estimate hours needed from lesson targets.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ---------------- Validation ----------------
    def clean(self):
        """
        Validate logical consistency for Goal fields before saving.

        Ensures:
            - At least one of weekly or milestone targets is provided.
            - Study days are within 1–7.
            - Milestone dates are not in the past.
            - Average hours per lesson and total lessons are positive if set.

        Raises:
            ValidationError: If any rule is violated.
        """
        super().clean()

        if (
            self.weekly_hours_target is None
            and self.weekly_lessons_target is None
            and self.total_required_lessons is None
        ):
            raise ValidationError(
                "Provide at least a weekly hours target, a weekly lessons"
                "target, or a milestone total."
            )

        if self.study_days_per_week < 1 or self.study_days_per_week > 7:
            raise ValidationError(
                "Study days per week must be between 1 and "
                "7."
            )

        if self.milestone_date and self.milestone_date < timezone.localdate():
            raise ValidationError(
                "Milestone date must be today or in the future."
            )

        if (
            self.avg_hours_per_lesson is not None
            and self.avg_hours_per_lesson <= 0
        ):
            raise ValidationError(
                "Average hours per lesson must be positive "
                "if provided."
            )

        if (
            self.total_required_lessons is not None
            and self.total_required_lessons == 0
        ):
            raise ValidationError(
                "Total required lessons must be greater than zero."
                )

    # ---------------- Derived targets ----------------
    @property
    def daily_hours_target(self):
        """If weekly hours target is set, divide by study days per week."""
        if self.weekly_hours_target is None:
            return None
        return float(self.weekly_hours_target) / self.study_days_per_week

    @property
    def daily_lessons_target(self):
        """If weekly lessons target is set, divide by study days per week."""
        if self.weekly_lessons_target is None:
            return None
        return self.weekly_lessons_target / self.study_days_per_week

    # ---------------- Milestone pacing helpers ----------------
    def weeks_until_milestone(self, today=None):
        """
        Return the number of whole or fractional weeks left until the
        milestone date.

        Args:
            today (date, optional): Date to calculate from (defaults to today).

        Returns:
            float | None: Weeks remaining, or None if no milestone date is set.
        """
        if not self.milestone_date:
            return None
        today = today or timezone.localdate()
        days = (self.milestone_date - today).days
        return max(0, days / 7)

    def lessons_per_week_to_hit_milestone(
            self,
            lessons_completed=0,
            today=None
    ):
        """
        Compute lessons per week required to meet the milestone by its date.

        Args:
            lessons_completed (int): Number of lessons already completed.
            today (date, optional): Current date (defaults to today).

        Returns:
            float | None: Lessons per week needed, or infinity if overdue.
        """
        if not self.total_required_lessons or not self.milestone_date:
            return None

        remaining = max(0, self.total_required_lessons - int(lessons_completed)
                        )
        weeks = self.weeks_until_milestone(today=today)

        if weeks is None or weeks == 0:
            return float("inf") if remaining > 0 else 0
        return remaining / weeks

    def hours_per_week_to_hit_milestone(self, lessons_completed=0, today=None):
        """
        Estimate required weekly hours to meet milestone based on
        avg_hours_per_lesson.

        Returns:
            float | None: Required hours per week, or None/infinity if
            insufficient data.
        """
        if self.avg_hours_per_lesson is None:
            return None

        lpw = self.lessons_per_week_to_hit_milestone(lessons_completed, today)
        if lpw in (None, float("inf")):
            return lpw

        return float(self.avg_hours_per_lesson) * lpw

    def daily_requirements_from_milestone(
            self,
            lessons_completed=0,
            today=None
    ):
        """
        Convert milestone pacing into daily values.

        Returns:
            tuple: (daily_lessons, daily_hours or None)
        """
        lpw = self.lessons_per_week_to_hit_milestone(lessons_completed, today)
        if lpw is None:
            return None, None

        daily_lessons = (
            float("inf")
            if lpw == float("inf")
            else lpw / self.study_days_per_week
        )
        hpw = self.hours_per_week_to_hit_milestone(lessons_completed, today)
        daily_hours = None
        if hpw is not None:
            daily_hours = (
                float("inf")
                if hpw == float("inf")
                else hpw / self.study_days_per_week
            )

        return daily_lessons, daily_hours

    # ---------------- Aggregations from StudySession ----------------
    def total_study_minutes(self):
        """
        Return total study minutes logged for this goal across all sessions.

        Returns:
            int: Sum of duration_minutes across linked StudySession objects.
        """
        from study_sessions.models import StudySession
        agg = (
            StudySession.objects
            .filter(goal=self)
            .aggregate(total=Sum("duration_minutes"))
        )
        return agg["total"] or 0

    def total_study_hours(self, decimals=1):
        """Return total lifetime study hours (rounded)."""
        return round(self.total_study_minutes() / 60, decimals)

    def weekly_study_minutes(self, today=None):
        """
        Return minutes logged for this goal in the current ISO week (Mon–Sun).

        Args:
            today (date, optional): Date for determining the current week.

        Returns:
            int: Total study minutes for this week.
        """
        from study_sessions.models import StudySession
        today = today or timezone.localdate()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=7)

        agg = (
            StudySession.objects.filter(
                goal=self,
                started_at__date__gte=week_start,
                started_at__date__lt=week_end,
            ).aggregate(total=Sum("duration_minutes"))
        )
        return agg["total"] or 0

    def weekly_progress_percent(self, today=None):
        """
        Calculate percentage progress toward weekly_hours_target.

        Returns:
            int | None: Progress percentage (0–100) or None if no target is
            set.
        """
        if self.weekly_hours_target is None:
            return None
        target_minutes = float(self.weekly_hours_target) * 60
        if target_minutes <= 0:
            return 0
        done = self.weekly_study_minutes(today)
        return min(100, round((done / target_minutes) * 100))

    def total_required_minutes(self):
        """
        Estimate total minutes required to finish this goal.

        Preferred calculation: avg_hours_per_lesson × total_required_lessons
        × 60.
        Returns None if insufficient data.

        Returns:
            int | None: Total required minutes, or None if unavailable.
        """
        if self.avg_hours_per_lesson and self.total_required_lessons:
            return int(
                float(self.avg_hours_per_lesson)
                * int(self.total_required_lessons)
                * 60
            )
        return None

    def total_required_hours(self, decimals=1):
        """Return estimated total required hours, or None if unknown."""
        minutes = self.total_required_minutes()
        if not minutes:
            return None
        return round(minutes / 60, decimals)

    def overall_progress_percent(self):
        """
        Return percentage of total estimated progress toward goal completion.

        Returns:
            int | None: Percentage (0–100), or None if total target unknown.
        """
        required = self.total_required_minutes()
        if not required or required <= 0:
            return None
        done = self.total_study_minutes()
        return min(100, round((done / required) * 100))

    def weekly_study_hours(self, decimals=1):
        """Return this week’s logged time in hours (rounded)."""
        return round(self.weekly_study_minutes() / 60, decimals)

    def projected_completion_date(self):
        """
        Estimate a completion date based on current average weekly pace.

        Returns:
            date | None: Predicted completion date, or None if
            insufficient data.
        """
        from study_sessions.models import StudySession

        total_required = self.total_required_minutes()
        if not total_required or total_required <= 0:
            return None

        done_minutes = self.total_study_minutes()
        if done_minutes == 0:
            return None

        qs = (
            StudySession.objects
            .filter(goal=self, started_at__isnull=False)
            .order_by("started_at")
        )
        first = qs.first()
        if not first:
            return None

        now = timezone.now()
        days_elapsed = (now - first.started_at).days or 1
        weeks_elapsed = days_elapsed / 7

        total_hours_done = done_minutes / 60
        pace_h_per_week = (
            total_hours_done / weeks_elapsed
            if weeks_elapsed > 0
            else None
        )
        if not pace_h_per_week or pace_h_per_week <= 0:
            return None

        total_required_hours = total_required / 60
        hours_remaining = max(0, total_required_hours - total_hours_done)
        weeks_remaining = hours_remaining / pace_h_per_week

        return (now + timedelta(weeks=weeks_remaining)).date()

    class Meta:
        ordering = ["-is_active", "-created_at"]
        constraints = [
            CheckConstraint(
                check=(
                    Q(study_days_per_week__gte=1)
                    & Q(study_days_per_week__lte=7),
                ),
                name="goals_days_between_1_and_7",
            ),
            CheckConstraint(
                check=(
                    Q(weekly_hours_target__isnull=False)
                    | Q(weekly_lessons_target__isnull=False)
                    | Q(total_required_lessons__isnull=False)
                ),
                name="goals_need_some_target",
            ),
        ]

    def __str__(self):
        """Return a human-readable string combining user, course, and
        milestone."""
        base = f"{self.user} Goal"
        if self.course:
            base += f" · {self.course.title}"
        if self.milestone_name:
            base += f" · {self.milestone_name}"
        return base


class GoalOutcome(models.Model):
    """
    Weekly frozen snapshot of a user's goal progress.

    Each GoalOutcome represents a single ISO week’s summary, storing
    both target and achieved values. Used for analytics and charting.
    """

    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        related_name="outcomes"
    )
    week_start = models.DateField()
    week_end = models.DateField()
    hours_completed = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=0
        )
    lessons_completed = models.PositiveIntegerField(default=0)
    hours_target = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True
        )
    lessons_target = models.PositiveIntegerField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["goal", "week_start"],
                name="unique_goal_week")
        ]
        ordering = ["-week_start"]

    def __str__(self):
        """Return a readable string showing goal name, week, and completion
        mark."""
        name = (
            self.goal.course.title
            if self.goal.course
            else self.goal.milestone_name
            or "General goal"
        )
        return f"{name} — {self.week_start} ({'✓' if self.completed else '✗'})"
