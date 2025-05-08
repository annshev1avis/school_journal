from django import forms
from django.core.exceptions import ValidationError

import apps.tests_app.models as models


class TaskSolutionForm(forms.ModelForm):
    class Meta:
        model = models.TaskSolution
        fields = ["student", "task", "result"]
        widgets = {
            "student": forms.HiddenInput,
            "task": forms.HiddenInput,
            "result": forms.NumberInput(attrs={"style": "width:100%"})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ограничивает возможные значения поля result
        self.fields["result"].widget.attrs["min"] = 0
        self.fields["result"].widget.attrs["max"] = self.instance.task.max_points

    def clean(self):
        cleaned_data = super().clean()
        
        # поле result находится в диапазоне допустимых значений
        if (
            cleaned_data["result"] and not 
            0 <= cleaned_data["result"] <= self.instance.task.max_points
        ):
            raise ValidationError(
                "Значение должно быть в диапазоне [0, "
                f"{self.instance.task.max_points}]"
            )
        
        return cleaned_data
        

class BaseStudentTestSolutionFormset(forms.BaseModelFormSet):
    def clean(self):
        """
        выполнят дополнительную проверку: 
        или должны быть заполнены все поля, 
        или все должны быть пустыми (когда ученик не писал тест)
        """
        if any(self.errors):
            return
        
        solutions = [
            form.cleaned_data["result"]
            for form in self.forms
        ]
        
        if not(
            all(solution is None for solution in solutions) or
            all(solution is not None for solution in solutions)
        ):
            raise ValidationError(
                "Если вы начали заполнять результаты ученика, "
                "надо заполнить поля для ВСЕХ заданий"
            )
            

        
"""
Используется для выставления ответов одного студента на один тест
"""
StudentTestSolutionFormSet = forms.modelformset_factory(
    models.TaskSolution,
    TaskSolutionForm,
    formset=BaseStudentTestSolutionFormset,
    extra=0,
)
