# apps/goals/forms.py
from django import forms
from .models import Goal
from courses.models import Course 

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
            "weekly_hours_target": forms.NumberInput(attrs={
                "step": "0.5", "min": "0", "inputmode": "decimal",
            }),
            "weekly_lessons_target": forms.NumberInput(attrs={
                "step": "1", "min": "0", "inputmode": "numeric",
            }),
            "study_days_per_week": forms.NumberInput(attrs={
                "step": "1", "min": "1", "max": "7", "inputmode": "numeric",
            }),
            "milestone_date": forms.DateInput(attrs={"type": "date"}),
            "avg_hours_per_lesson": forms.NumberInput(attrs={
                "step": "0.25", "min": "0", "inputmode": "decimal",
            }),
        }
        labels = {
            "course": "Course",
            "weekly_hours_target": "Weekly hours",
            "weekly_lessons_target": "Weekly lessons",
            "study_days_per_week": "Study days per week",
            "total_required_lessons": "Total lessons",
            "milestone_name": "Milestone name",
            "milestone_date": "Milestone date",
            "avg_hours_per_lesson": "Avg hours per lesson",
            "is_active": "Is active",
        }
        help_texts = {
            "weekly_hours_target": "",
            "weekly_lessons_target": "",
            "study_days_per_week": "",
            "total_required_lessons": "",
            "milestone_name": "",
            "milestone_date": "",
            "avg_hours_per_lesson": "",
            "is_active": "",
            "course": "",
        }


    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Only show this user's courses in the dropdown
        if "course" in self.fields:
            if user is not None:
                self.fields["course"].queryset = Course.objects.filter(owner=user)
            else:
                # If no user provided, don't expose all courses
                self.fields["course"].queryset = Course.objects.none()

    def clean(self):
        cleaned = super().clean()
        weekly_hours = cleaned.get("weekly_hours_target")
        weekly_lessons = cleaned.get("weekly_lessons_target")
        total_required = cleaned.get("total_required_lessons")
        study_days = cleaned.get("study_days_per_week")

        # Require at least one target (weekly hours OR weekly lessons OR milestone total)
        if weekly_hours is None and weekly_lessons is None and total_required is None:
            raise forms.ValidationError(
                "Please set a weekly hours target, weekly lessons target, or a milestone total."
            )

        # Extra guard; model also has a CheckConstraint for this.
        if study_days is not None and not (1 <= study_days <= 7):
            self.add_error("study_days_per_week", "Study days per week must be between 1 and 7.")

        return cleaned
