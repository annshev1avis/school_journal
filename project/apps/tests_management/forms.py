from django import forms

from apps.core.models import Group
from apps.tests_management import models


class TestForm(forms.ModelForm):
    class Meta:
        model = models.Test
        fields = [
            "name", "subject", "studing_year", "month",
        ]


class TaskForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = ["id", "num", "level", "checked_skill", "max_points"]
        widgets = {
            "id": forms.HiddenInput,
        }


class GroupsForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(),
        widget=forms.CheckboxSelectMultiple,
    )

class AddGroupsForm(GroupsForm):
    def __init__(self, test, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["groups"].queryset = Group.objects.exclude(testassign__test=test)


class RemoveGroupsForm(GroupsForm):
    def __init__(self, test, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["groups"].queryset = Group.objects.filter(
            testassign__test=test, testassign__writing_date__isnull=True
        )
        

TaskFormSet = forms.inlineformset_factory(
    models.Test,
    models.Task,
    form=TaskForm,
    extra=0,
    can_delete=True,
)
