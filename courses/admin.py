from django.contrib import admin
from .models import Course

# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "status", "start_date", "end_date", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "provider", "owner__email", "owner__username")
    autocomplete_fields = ("owner",)