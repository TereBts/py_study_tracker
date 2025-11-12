# apps/goals/forms.py
from django import forms
from .models import Goal
from courses.models import Course


class GoalForm(forms.ModelForm):
    """
    Form for creating and updating user study goals.

    This form allows users to define their study targets — such as weekly
    hours,
    number of lessons, total lessons, milestone name/date, and average
    hours per lesson.
    It also enforces that only the logged-in user’s own courses appear
    in the dropdown list and validates logical input constraints.

    Features:
        - Dynamically filters the 'course' field to the user’s courses.
        - Validates that at least one study target is provided.
        - Enforces 'study_days_per_week' within the valid 1–7 range.
        - Provides user-friendly widgets and labels for clarity.

    Meta:
        model (Goal): The model associated with this form.
        fields (list): The editable fields in the Goal model.
        widgets (dict): Custom HTML input types for number/date fields.
        labels (dict): Human-readable field labels.
        help_texts (dict): Minimal guidance text (empty for cleaner UI).
    """

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
        help_texts = {field: "" for field in fields}

    def __init__(self, *args, user=None, **kwargs):
        """
        Initialize the form and filter the 'course' field for the given user.

        Args:
            *args: Standard positional arguments for ModelForm.
            user (User, optional): The currently logged-in user; used to limit
                the course queryset so users only see their own courses.
            **kwargs: Standard keyword arguments for ModelForm.
        """
        super().__init__(*args, **kwargs)

        # Restrict available courses to those owned by the current user
        if "course" in self.fields:
            if user is not None:
                self.fields["course"].queryset = Course.objects.filter(
                    owner=user
                )
            else:
                # Prevent displaying all courses if no user context provided
                self.fields["course"].queryset = Course.objects.none()

    def clean(self):
        """
        Validate form data for logical consistency.

        Ensures:
            - At least one target (weekly hours, weekly lessons, or total
            lessons)
              is specified.
            - The 'study_days_per_week' value is between 1 and 7 inclusive.

        Raises:
            ValidationError: If no study targets are provided or if invalid
            values
            are entered for study days.

        Returns:
            dict: The cleaned and validated form data.
        """
        cleaned = super().clean()
        weekly_hours = cleaned.get("weekly_hours_target")
        weekly_lessons = cleaned.get("weekly_lessons_target")
        total_required = cleaned.get("total_required_lessons")
        study_days = cleaned.get("study_days_per_week")

        # Require at least one target metric
        if (
            weekly_hours is None
            and weekly_lessons is None
            and total_required is None
        ):
            raise forms.ValidationError(
                "Please set a weekly hours target, weekly lessons target, "
                "or a milestone total."
            )

        # Ensure study days are within the 1–7 valid range
        if study_days is not None and not (1 <= study_days <= 7):
            self.add_error(
                "study_days_per_week", "Study days per week must be between "
                "1 and 7."
            )

        return cleaned
