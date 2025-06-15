from django import forms
from django.core import validators
from django.db import transaction

from apps.core.models import Group
from apps.tests_management import models


class TestCreateForm(forms.ModelForm):
    class Meta:
        model = models.Test
        fields = [
            "name", "subject", "with_reflexive_level", "studing_year", "month",
        ]
        

class TestUpdateForm(forms.ModelForm):
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
      

class DualTaskForm(forms.Form):
    """
    Форма для работы сразу с 2 объектами models.Task.
    Имеет общие поля: num, checked_skill, которые одинаково сохраняются в 2 заданиях
    и одно различное поле для количества баллов (basic_max_points и reflexive_max_points)
    """
    num = forms.IntegerField(label="Номер", min_value=1)
    checked_skill = forms.CharField(label="Проверяемый навык", max_length=300)
    basic_max_points = forms.IntegerField(label="Макс. балл (баз)", min_value=1)
    reflexive_max_points = forms.IntegerField(label="Макс. балл (реф)", min_value=1)

    def __init__(self, *args, test, basic_instance=None, reflexive_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.test = test
        self.basic_instance = basic_instance
        self.reflexive_instance = reflexive_instance

        # Установим initial-значения, если редактируем
        if basic_instance:
            self.fields['num'].initial = basic_instance.num
            self.fields['checked_skill'].initial = basic_instance.checked_skill
            self.fields['basic_max_points'].initial = basic_instance.max_points

        if reflexive_instance:
            self.fields['reflexive_max_points'].initial = reflexive_instance.max_points

    def save(self):
        data = self.cleaned_data
        with transaction.atomic():
            # BASIC
            basic = self.basic_instance or models.Task(
                test=self.test, level=models.Task.BASIC
            )
            basic.num = data["num"]
            basic.checked_skill = data["checked_skill"]
            basic.max_points = data["basic_max_points"]
            basic.save()

            # REFLEXIVE
            reflexive = self.reflexive_instance or models.Task(
                test=self.test, level=models.Task.REFLEXIVE
            )
            reflexive.num = data["num"]
            reflexive.checked_skill = data["checked_skill"]
            reflexive.max_points = data["reflexive_max_points"]
            reflexive.save()

        return basic, reflexive

    def delete(self):
        self.basic_instance.delete()
        self.reflexive_instance.delete()

    @property
    def has_instances(self):
        return self.basic_instance is not None and self.reflexive_instance is not None


class TaskCleanMixin:
    def clean(self):
        if any(self.errors):
            return

        nums = []
        for form in self.forms:
            num = form.cleaned_data.get('num')
            if num in nums:
                raise forms.ValidationError("Номера заданий не должны повторяться.")
            nums.append(num)


class BaseDualTaskFormSet(TaskCleanMixin, forms.BaseFormSet):
    deletion_widget = forms.HiddenInput(attrs={"class": "deletion-widget"})
    
    def __init__(self, *args, instance, queryset=None, **kwargs):
        self.instance = instance
        self.queryset = queryset or self.instance.tasks.all()
        self.dual_instances = []  # список пар (basic, reflexive)
        
        # Группируем по num
        grouped = {}
        for task in self.queryset:
            grouped.setdefault(task.num, {})[task.level] = task

        self.dual_instances = [
            (group.get(models.Task.BASIC), group.get(models.Task.REFLEXIVE)) 
            for group in grouped.values()
        ]

        kwargs['initial'] = []
        for basic, reflexive in self.dual_instances:
            initial_data = {}
            if basic:
                initial_data.update({
                    'num': basic.num,
                    'checked_skill': basic.checked_skill,
                    'basic_max_points': basic.max_points,
                })
            if reflexive:
                initial_data.update({
                    'reflexive_max_points': reflexive.max_points,
                })
            kwargs['initial'].append(initial_data)

        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        if index < len(self.dual_instances):
            basic, reflexive = self.dual_instances[index]
        else:
            basic = reflexive = None
        kwargs.update({
            'test': self.instance,
            'basic_instance': basic,
            'reflexive_instance': reflexive,
        })
        return kwargs

    def save(self):
        for form in self.forms:
            if form.has_changed() and form.is_valid():
                form.save()
                
        for form in self.deleted_forms:
            if form.has_instances:
                form.delete()


class BaseTaskFormSet(forms.BaseInlineFormSet, TaskCleanMixin):
    deletion_widget = forms.HiddenInput(attrs={"class": "deletion-widget"})
    
    
TaskFormset = forms.inlineformset_factory(
    parent_model=models.Test,
    model=models.Task,
    formset=BaseTaskFormSet,
    fields=["num", "checked_skill", "max_points"],
    extra=1,
    can_delete=True,
)

DualTaskFormset = forms.formset_factory(
    DualTaskForm,
    formset=BaseDualTaskFormSet,
    extra=1,
    can_delete=True,
)
