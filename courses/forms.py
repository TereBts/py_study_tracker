# courses/forms.py
from django import forms
from .models import Course


class DateInput(forms.DateInput):
    """
    Custom form widget for selecting dates.

    This subclass of Django’s built-in DateInput sets the input type
    to "date", enabling HTML5 date pickers in modern browsers.

    Example:
        Used for start_date and end_date fields in the CourseForm.
    """

    input_type = "date"  # HTML5 date input


class CourseForm(forms.ModelForm):
    """
    Form for creating and editing Course instances.

    This form allows users to define their own courses with title,
    provider, description, duration, status, and colour selection.
    It automatically restricts duplicate titles per user and provides
    date picker widgets for start and end dates.

    Meta:
        - model: Course
        - fields: Main editable attributes of the course.
        - widgets: Customizes input presentation (radio buttons for colour
          and HTML5 date inputs for date fields).

    The form also accepts a `user` keyword argument to scope validation
    to the currently logged-in user.
    """

    class Meta:
        model = Course
        fields = [
            "title",
            "provider",
            "description",
            "start_date",
            "end_date",
            "status",
            "colour",
        ]
        widgets = {
            "colour": forms.RadioSelect,
            "start_date": DateInput(format="%Y-%m-%d"),
            "end_date": DateInput(format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the CourseForm and apply user-specific validation context.

        Args:
            *args: Standard positional arguments for ModelForm.
            **kwargs: Can include a 'user' keyword argument, which is stored
                on the form instance and used in validation to prevent
                duplicate
                course titles for the same user.
        """
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["start_date"].input_formats = ["%Y-%m-%d"]
        self.fields["end_date"].input_formats = ["%Y-%m-%d"]

    def clean_title(self):
        """
        Ensure the course title is unique for the current user.

        Performs a case-insensitive check to prevent users from creating
        multiple courses with the same title. If an existing course matches,
        a ValidationError is raised.

        Returns:
            str: The cleaned and validated course title.
        """
        title = self.cleaned_data["title"].strip()
        if self.user:
            qs = Course.objects.filter(owner=self.user, title__iexact=title)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    "You already have a course with this title."
                )
        return title
