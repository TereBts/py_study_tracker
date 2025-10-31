from django import forms
from .models import Goal

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = [
            "course",
            "weekly_hours_target",
            "weekly_lessons_target",
            "study_days_per_week",
            "total_required_lessons",
            "milestone_name",
            "milestone_date",
            "avg_hours_per_lesson",
            "is_active",
        ]
        widgets = {
            "milestone_date": forms.DateInput(attrs={"type": "date"}),  # gives users a date picker
        }

    def clean(self):
        cleaned = super().clean()
        weekly_hours = cleaned.get("weekly_hours_target")
        weekly_lessons = cleaned.get("weekly_lessons_target")
        total_required = cleaned.get("total_required_lessons")

        if weekly_hours is None and weekly_lessons is None and total_required is None:
            raise forms.ValidationError(
                "Please set a weekly hours target, weekly lessons target, or a milestone total."
            )

        return cleaned