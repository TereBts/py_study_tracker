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