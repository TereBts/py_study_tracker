from django import forms
from .models import Course

class ColourRadio(forms.RadioSelect):
    # Custom templates for the radio group and each option
    template_name = "widgets/colour_radio.html"
    option_template_name = "widgets/colour_radio_option.html"

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "provider", "description", "start_date", "end_date", "status", "colour"]
        widgets = {
            "colour": ColourRadio,   # ⬅️ use the radio palette instead of a <select>
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
