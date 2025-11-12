"""Course models and enums for StudyStar.

Defines the Course model, its status/colour choices, and helper methods
for validation, URL generation, and active-state checks.
"""

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone


class CourseColour(models.TextChoices):
    """
    Enum of colour choices used to visually categorise courses.

    Values are stored as hex strings for direct use in CSS, with
    human-friendly labels for admin/forms.
    """

    INDIGO = "#6366F1", "Indigo"
    VIOLET = "#7C3AED", "Violet"
    EMERALD = "#10B981", "Emerald"
    SKY = "#0EA5E9", "Sky"
    AMBER = "#F59E0B", "Amber"
    ROSE = "#F43F5E", "Rose"
    SLATE = "#475569", "Slate"
    NONE = "", "No colour"


class Course(models.Model):
    """
    Represents a user-owned course with optional dates, status, and colour.

    A Course belongs to a single owner (the creating user) and can be shown
    on dashboards, filtered by status, and colour-coded. Slugs are generated
    per owner to produce clean, predictable URLs.

    Constraints:
        - Unique (owner, title): prevents duplicate course titles per user.

    Default ordering:
        - Newest first (by created_at).
    """

    class Status(models.TextChoices):
        """
        Enum of lifecycle states for a course.

        Used to indicate whether the course is planned, active, paused,
        or completed. Backed by fixed string values to keep URLs stable
        and filtering efficient.
        """

        PLANNED = "planned", "Planned"
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        COMPLETED = "completed", "Completed"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        help_text="User who owns/created this course.",
    )
    title = models.CharField(max_length=120, help_text="Name of the course.")
    provider = models.CharField(
        max_length=120, blank=True, help_text="Optional provider, e.g., "
        "Coursera."
    )
    description = models.TextField(
        blank=True,
        help_text=(
            "Optional course "
            "details."
        )
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Optional start date."
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Optional end date."
    )

    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PLANNED,
        help_text="Current lifecycle state of the course.",
    )

    colour = models.CharField(
        max_length=9,
        choices=CourseColour.choices,
        blank=True,
        default=CourseColour.NONE,
        help_text="Optional colour used in UI to distinguish courses.",
    )

    slug = models.SlugField(
        max_length=140,
        blank=True,
        editable=False,
        help_text="URL slug (auto-generated)."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp."
        )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp."
        )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "title"], name="uniq_owner_title_per_course"
            ),
        ]

    def __str__(self):
        """
        Return a human-readable name for admin and shell displays.

        Returns:
            str: The course title.
        """
        return self.title

    def clean(self):
        """
        Validate field relationships before saving.

        Ensures the end date, when provided, is not earlier than the
        start date.

        Raises:
            ValidationError: If end_date is before start_date.
        """
        if (
            self.start_date
            and self.end_date
            and self.end_date < self.start_date
        ):

            raise ValidationError({
                "end_date": "End date can’t be before start date."
            })

    def save(self, *args, **kwargs):
        """
        Persist the course, auto-generating a unique slug per owner if missing.

        Slug is derived from the title (URL-safe) and made unique by appending
        an incrementing suffix (-2, -3, …) if a clash exists for the same
        owner.
        """
        if not self.slug:
            base = slugify(self.title)[:120]
            self.slug = base
            i = 2
            while Course.objects.filter(
                owner=self.owner, slug=self.slug
            ).exclude(pk=self.pk).exists():
                self.slug = f"{base}-{i}"
                i += 1
        super().save(*args, **kwargs)

    def is_active(self):
        """
        Determine if the course is currently active.

        A course is considered active when:
          - status is ACTIVE, and
          - today is on/after start_date (if set), and
          - today is on/before end_date (if set).

        Returns:
            bool: True if active by the above rules, else False.
        """
        if self.status != self.Status.ACTIVE:
            return False
        today = timezone.localdate()
        if self.start_date and self.start_date > today:
            return False
        if self.end_date and self.end_date < today:
            return False
        return True

    def get_absolute_url(self):
        """
        Return the canonical URL for this course detail page.

        Used by Django’s admin and generic redirects after create/update.

        Returns:
            str: Resolved URL path for the course detail route.
        """
        return reverse("courses:detail", kwargs={"slug": self.slug})
