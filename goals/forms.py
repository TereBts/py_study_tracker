# apps/goals/forms.py
from django import forms
from .models import Goal

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = [
            "course",
            "weekly_hours_target",      # decimal, validated in model to 0.5 steps
            "weekly_lessons_target",    # remove if not in your model
            "study_days_per_week",
            "total_required_lessons",
            "milestone_name",
            "milestone_date",
            "avg_hours_per_lesson",
            "is_active",
        ]
        widgets = {
            # Guide browser input to 0.5 steps; model validator still enforces it.
            "weekly_hours_target": forms.NumberInput(attrs={
                "step": "0.5",
                "min": "0",
                "inputmode": "decimal",
            }),
            # Weekly lessons as whole numbers (remove if field not in model)
            "weekly_lessons_target": forms.NumberInput(attrs={
                "step": "1",
                "min": "0",
                "inputmode": "numeric",
            }),
            # Keep days between 1–7
            "study_days_per_week": forms.NumberInput(attrs={
                "step": "1",
                "min": "1",
                "max": "7",
                "inputmode": "numeric",
            }),
            "milestone_date": forms.DateInput(attrs={"type": "date"}),
            # Let users put quarter-hour granularity if they want; model can be looser/tighter.
            "avg_hours_per_lesson": forms.NumberInput(attrs={
                "step": "0.25",
                "min": "0",
                "inputmode": "decimal",
            }),
        }

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
