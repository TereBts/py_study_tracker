from django.contrib import admin
from .models import StudySession

# Register your models here.
@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "goal", "started_at", "duration_minutes")
    list_filter = ("course", "goal", "started_at")
    search_fields = ("user__username", "course__title", "notes")
    autocomplete_fields = ("user", "course", "goal")