from django import forms
from django.core.exceptions import ValidationError

import apps.tests_app.models as models
from apps.tests_management.models import Task, TestAssign


class TestAssignForm(forms.ModelForm):
    class Meta:
        model = TestAssign
        fields = ["writing_date"]
        widgets = {
            "writing_date": forms.DateInput(attrs={'type': 'date'}, format="%Y-%m-%d"),
        }


class TaskSolutionForm(forms.ModelForm):
    class Meta:
        model = models.TaskSolution
        fields = ["student", "task", "result"]
        widgets = {
            "student": forms.HiddenInput,
            "task": forms.HiddenInput,
            "result": forms.NumberInput
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
        if not len(self.forms) > 0:
            return
        
        self.test = self.get_test()
        new_results = self.get_new_results()
        
        self.check_filled_in_full(new_results)
        if self.is_filled and self.test.with_reflexive_level:
            self.check_levels_are_consistent(new_results)
    
    def get_test(self):
        return self.forms[0].instance.task.test
            
    def get_new_results(self):
        return {
            form.instance.task: form.cleaned_data["result"] for form in self.forms
        }
    
    def check_filled_in_full(self, new_results):
        """
        Проверяет, что результаты теста не были заполнены частично
        """
        if not (
            all(res is None for res in new_results.values()) or
            all(res is not None for res in new_results.values())
        ):
            raise ValidationError(
                "Если вы начали заполнять результаты ученика, "
                "надо заполнить поля для ВСЕХ заданий"
            )
            
        self.is_filled = all(res is not None for res in new_results.values())

    def check_levels_are_consistent(self, new_results):
        """
        Проверяет, что баллы за задания базового и рефлексивного уровней
        находятся в согласованном состоянии. (Согласно системе оценивания,
        если ученик решил рефлексивное задание, соответствующее задание
        базового уровня защитывается на максимальный балл автоматически)
        """
        nums = self.queryset.values_list("task__num", flat=True).distinct()
        
        for num in nums:
            basic_task = Task.objects.get(
                test=self.test, num=num, level=Task.BASIC
            )
            reflexive_task = Task.objects.get(
                test=self.test, num=num, level=Task.REFLEXIVE
            )
            
            basic_task_has_max_points = (
                new_results[basic_task] == basic_task.max_points
            )
            reflexive_task_has_points = new_results[reflexive_task] > 0
            
            if reflexive_task_has_points and (not basic_task_has_max_points):
                raise ValidationError(
                    f"""В задании #{num} базовый уровень должен
                    быть оценен на максимум, так как
                    решён рефлексивный"""
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
