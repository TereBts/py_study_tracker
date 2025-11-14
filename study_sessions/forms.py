# study_sessions/forms.py
from django import forms
from .models import StudySession
from courses.models import Course
from goals.models import Goal


class StudySessionForm(forms.ModelForm):
    """
    Form for creating and updating StudySession records.

    Allows users to log individual study sessions, linking them to
    a specific course and goal. The form automatically filters both
    course and goal fields to only show options that belong to the
    logged-in user.
    """

    class Meta:
        model = StudySession
        fields = ["course", "goal", "started_at", "duration_minutes", "notes"]
        widgets = {
            "started_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # REMOVE ALL HELP TEXT FROM FORM FIELDS
        for field in self.fields.values():
            field.help_text = ""

        # Filter user-specific dropdowns
        if user is not None:
            self.fields["course"].queryset = Course.objects.filter(owner=user)
            self.fields["goal"].queryset = Goal.objects.filter(
                user=user, is_active=True
            )

    def clean_duration_minutes(self):
        mins = self.cleaned_data["duration_minutes"]
        if mins < 1:
            raise forms.ValidationError("Duration must be at least 1 minute.")
        return mins
