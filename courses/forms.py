# courses/forms.py
from django import forms
from .models import Course

class DateInput(forms.DateInput):
    input_type = "date"  # HTML5 date input

class CourseForm(forms.ModelForm):
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
        # use Django’s standard RadioSelect for colour
        widgets = {
            "colour": forms.RadioSelect,
            "start_date": DateInput(format="%Y-%m-%d"),
            "end_date": DateInput(format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["start_date"].input_formats = ["%Y-%m-%d"]
        self.fields["end_date"].input_formats = ["%Y-%m-%d"]

    def clean_title(self):
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
