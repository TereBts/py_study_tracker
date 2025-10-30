from django import forms
from .models import Course

class ColourSelect(forms.Select):
    """
    Progressive enhancement:
    - Adds a data-colour attr for each <option> so JS can read hex easily.
    - set an inline style on the option
    to show a small colour swatch in browsers that support it.
    """
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        hexval = option["value"] or ""
        if hexval:
            option["attrs"]["data-colour"] = hexval
            option["attrs"]["style"] = f"background-image: linear-gradient(90deg,{hexval} 0 1rem,transparent 1rem);"
        return option

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "provider", "description", "start_date", "end_date", "status", "colour"]
        widgets = {
            "colour": ColourSelect(),  # our custom widget
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
