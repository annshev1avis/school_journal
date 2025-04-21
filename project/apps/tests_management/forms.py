from django import forms

from apps.tests_management import models


class TestForm(forms.ModelForm):
    class Meta:
        model = models.Test
        fields = [
            "name", "subject", "studing_year", "groups"
        ]
        widgets = {
            "groups": forms.CheckboxSelectMultiple
        }


TaskFormSet = forms.inlineformset_factory(
    models.Test,
    models.Task, 
    extra=2,
    fields = [
        "num", "sub_num", "checked_skill", "max_points",
    ]
)
