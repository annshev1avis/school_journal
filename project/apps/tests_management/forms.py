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


class TaskForm(forms.ModelForm):
    class Meta:
        model = models.Task  # Убедитесь, что импортировали модель Task
        fields = ['id', 'num', 'sub_num', 'checked_skill', 'max_points']
        widgets = {
            'id': forms.HiddenInput,
        }


TaskFormSet = forms.inlineformset_factory(
    models.Test,
    models.Task,
    form=TaskForm,
    extra=0,
    can_delete=True,
)
