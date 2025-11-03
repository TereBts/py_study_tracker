from django import forms
from .models import StudySession

class StudySessionForm(forms.ModelForm):
    class Meta:
        model = StudySession
        fields = ["course", "goal", "started_at", "duration_minutes", "notes"]
        widgets = {
            "started_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_duration_minutes(self):
        mins = self.cleaned_data["duration_minutes"]
        if mins < 1:
            raise forms.ValidationError("Duration must be at least 1 minute.")
        return mins
