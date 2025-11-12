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

    Features:
        - HTML5 datetime-local widget for the 'started_at' field.
        - Textarea for notes.
        - Validation to ensure duration is at least one minute.

    Meta:
        model (StudySession): The model associated with this form.
        fields (list): Fields editable by users.
        widgets (dict): Custom HTML widgets for improved UX.
    """

    class Meta:
        model = StudySession
        fields = ["course", "goal", "started_at", "duration_minutes", "notes"]
        widgets = {
            "started_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        """
        Initialize the form and limit selectable courses and goals
        to those owned by the current user.

        Args:
            *args: Positional arguments passed to ModelForm.
            user (User, optional): The currently authenticated user.
                If provided, restricts 'course' and 'goal' dropdowns to
                items owned by this user.
            **kwargs: Standard keyword arguments for ModelForm.
        """
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields["course"].queryset = Course.objects.filter(owner=user)
            self.fields["goal"].queryset = Goal.objects.filter(user=user, is_active=True)
        # If no user provided (e.g. in admin), default queryset remains unrestricted.

    def clean_duration_minutes(self):
        """
        Validate that the session duration is a positive integer.

        Raises:
            ValidationError: If duration is less than 1 minute.

        Returns:
            int: The validated duration in minutes.
        """
        mins = self.cleaned_data["duration_minutes"]
        if mins < 1:
            raise forms.ValidationError("Duration must be at least 1 minute.")
        return mins
