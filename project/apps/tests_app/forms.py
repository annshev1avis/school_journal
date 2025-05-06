from django import forms

import apps.tests_app.models as models


class TaskSolutionForm(forms.ModelForm):
    class Meta:
        model = models.TaskSolution
        fields = ["student", "task", "result"]
        widgets = {
            "student": forms.HiddenInput,
            "task": forms.HiddenInput,
        }
    

"""
Используется для выставления ответов одного студента на один тест
"""
StudentTestSolutionFormSet = forms.modelformset_factory(
    models.TaskSolution,
    TaskSolutionForm,
    extra=0,
)
