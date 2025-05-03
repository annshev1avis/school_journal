from django import forms


class TaskSolutionForm(forms.ModelForm):
    fields = ["student", "task", "result"]
    widgets = {
        "student": forms.HiddenInput,
        "task": forms.HiddenInput,
    }

TaskSolutionFormSet = forms.formset_factory(TaskSolutionForm)
