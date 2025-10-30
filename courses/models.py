from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.

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
        blank=True,
        help_text="Optional hex like #7C3AED",
    )


    