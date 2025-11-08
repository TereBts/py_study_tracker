# study_sessions/forms.py
from django import forms
from .models import StudySession
from courses.models import Course
from goals.models import Goal


class StudySessionForm(forms.ModelForm):
    class Meta:
        model = StudySession
        fields = ["course", "goal", "started_at", "duration_minutes", "notes"]
        widgets = {
            "started_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None:
            # Use owner for courses
            self.fields["course"].queryset = Course.objects.filter(owner=user)

            # Goals are tied to user
            self.fields["goal"].queryset = Goal.objects.filter(user=user, is_active=True)
        # If no user passed (e.g. admin), leave defaults or adjust as needed.

    def clean_duration_minutes(self):
        mins = self.cleaned_data["duration_minutes"]
        if mins < 1:
            raise forms.ValidationError("Duration must be at least 1 minute.")
        return mins
