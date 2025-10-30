from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.
# Define a set of colour choices for course categorization.
class CourseColour(models.TextChoices):
    INDIGO = "#6366F1", "Indigo"
    VIOLET = "#7C3AED", "Violet"
    EMERALD = "#10B981", "Emerald"
    SKY    = "#0EA5E9", "Sky"
    AMBER  = "#F59E0B", "Amber"
    ROSE   = "#F43F5E", "Rose"
    SLATE  = "#475569", "Slate"
    NONE   = "", "No colour"

class Course(models.Model):
    # Define possible status values using Django’s TextChoices helper.
    # This gives both human-friendly labels and fixed database values.
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        COMPLETED = "completed", "Completed"

    # Link each course to the user who created it.
    # settings.AUTH_USER_MODEL makes it compatible with custom user models.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,         # If a user is deleted, delete their courses too.
        related_name="courses",           # Enables user.courses.all() lookups.
    )

    # Core descriptive fields for the course.
    title = models.CharField(max_length=120)
    provider = models.CharField(max_length=120, blank=True)  # Optional (e.g., Coursera, Udemy).
    description = models.TextField(blank=True)

    # Optional date fields to record when a course runs.
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Track overall progress state of the course.
    status = models.CharField(
        max_length=12,
        choices=Status.choices,           # Restrict values to the Status options above.
        default=Status.PLANNED,
    )

    # Optional colour field to visually differentiate courses on dashboards.
    colour = models.CharField(
            max_length=9,
            choices=CourseColour.choices,
            blank=True,
            default=CourseColour.NONE,
        )

    # Slug creates clean, human-readable URLs like /courses/python-basics/
    slug = models.SlugField(max_length=140, blank=True, editable=False)

    # Automatically record when a course is created or last updated.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Default ordering: newest courses first.
        ordering = ["-created_at"]

        # Prevent duplicate course titles for the same owner.
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "title"], name="uniq_owner_title_per_course"
            ),
        ]

    # The string representation shown in admin and shell queries.
    def __str__(self):
        return self.title

    # Custom validation that runs before saving via .full_clean()
    def clean(self):
        # Ensure end_date isn't earlier than start_date.
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date can’t be before start date."})

    # Override save() to automatically generate a unique slug for each user.
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:120]  # Convert title into URL-safe form.
            self.slug = base
            i = 2
            # Ensure slug uniqueness per owner (append -2, -3, etc. if needed).
            while Course.objects.filter(owner=self.owner, slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base}-{i}"
                i += 1
        # Call the original save() to actually write to the database.
        super().save(*args, **kwargs)

    # Convenience method to check if a course is currently active.
    def is_active(self):
        if self.status != self.Status.ACTIVE:
            return False
        today = timezone.localdate()
        # Not active yet if start_date is in the future.
        if self.start_date and self.start_date > today:
            return False
        # No longer active if end_date has passed.
        if self.end_date and self.end_date < today:
            return False
        return True

    # Provides a standard URL for a course instance, used in redirects and links.
    def get_absolute_url(self):
        return reverse("courses:detail", kwargs={"slug": self.slug})


    