# courses/forms.py
from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "provider", "description", "start_date", "end_date", "status", "colour"]
        widgets = {
            "colour": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if self.user:
            qs = Course.objects.filter(owner=self.user, title__iexact=title)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("You already have a course with this title.")
        return title
