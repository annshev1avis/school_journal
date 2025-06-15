import random

from django.db import transaction
from django.contrib import messages
from django.views import generic
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from apps.core.views import ListFiltersMixin
from apps.tests_app.models import TaskSolution
from apps.tests_management import forms
from apps.tests_management import models


# список тестов
class TestListView(ListFiltersMixin, generic.ListView):
    model = models.Test
    template_name = "tests_management/tests_list.html"
    context_object_name = "tests"
    filter_fields = ["studing_year", "subject"]


# операции с отдельным тестом
class TestCreateView(generic.CreateView):
    model = models.Test
    template_name = "tests_management/create_test.html"
    form_class = forms.TestForm
    
    def get_success_url(self):
        return reverse_lazy(
            "tests_management:update_test",
            kwargs={"pk": self.object.pk}
        )


class TestDetailView(generic.DetailView):
    model = models.Test
    template_name = "tests_management/test_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["add_groups_form"] = forms.AddGroupsForm(self.get_object())
        context["remove_groups_form"] = forms.RemoveGroupsForm(test=self.get_object())

        return context

class TestWithTasksUpdateView(generic.View):
    template_name = "tests_management/update_test.html"
    
    def get_tasks_formset(self, test, post_data=None):
        formset_class = forms.DualTaskFormset if test.with_reflexive_level else forms.TaskFormset
        return formset_class(
            data=post_data if post_data else None,
            instance=test,
            queryset=test.tasks.order_by("num"),
            prefix="form"
        )
    
    def get(self, request, pk):
        test = get_object_or_404(models.Test, pk=pk)
        
        test_form = forms.TestForm(instance=test)
        tasks_formset = self.get_tasks_formset(test)
    
        return render(
            request,
            self.template_name,
            {
                "test": test,
                "test_form": test_form,
                "tasks_formset": tasks_formset,
                "test_assigns": models.TestAssign.objects.filter(test=test),
            }
        )

    def post(self, request, pk):
        test = get_object_or_404(models.Test, pk=pk)
        
        test_form = forms.TestForm(request.POST, instance=test)
        tasks_formset = self.get_tasks_formset(test, post_data=request.POST)
        
        if test_form.is_valid() and tasks_formset.is_valid():
            test = test_form.save()
            tasks_formset.save()
                
            messages.success(request, "Изменения сохранены")
            return redirect(reverse_lazy("tests_management:update_test", kwargs={"pk": test.pk}))
        
        print(tasks_formset.is_valid(), tasks_formset.non_form_errors(), tasks_formset.errors)
        messages.error(request, "Ошибки при заполнении формы")
        return render(
            request,
            self.template_name,
            {
                "test": test,
                "test_form": test_form,
                "tasks_formset": tasks_formset,
                "test_assigns": models.TestAssign.objects.filter(test=test),
            }
        )


class TestDeleteView(generic.DeleteView):
    model = models.Test
    template_name = "tests_management/test_confirm_delete.html"
    success_url = reverse_lazy("tests_management:tests_list")


# операции с отдельным заданием
class TaskCreateView(generic.CreateView):
    model = models.Task
    fields = ["num", "level", "checked_skill", "max_points"]
    template_name = "tests_management/task_form.html"
    
    def setup(self, request, *args, **kwargs):
        # инициализация выполняется для всех типов запросов
        super().setup(request, *args, **kwargs)
        self.test = models.Test.objects.get(pk=kwargs["test_pk"])
    
    def form_valid(self, form):
        form.instance.test = self.test
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy("tests_management:update_test", kwargs={"pk": self.object.test.pk})


class PublishTestView(generic.DetailView):
    model = models.Test
    
    def post(self, request, *args, **kwargs):
        test = self.get_object()
        test.is_published = True
        test.save()
        
        messages.success(request, 'Тест успешно опубликован!')
        return redirect(reverse_lazy("tests_management:test_detail", args=[test.pk]))
    
    
class GroupsView(generic.DetailView):
    model = models.Test
    success_message = "Успешно!"
    
    def do_action(self, groups):
        raise NotImplementedError
    
    def get_form(self):
        raise NotImplementedError
    
    def post(self, request, *args, **kwargs):
        self.test = self.get_object()
        groups_form = self.get_form()
        
        if groups_form.is_valid():
            groups_list = list(groups_form.cleaned_data["groups"])
            self.do_action(groups_list)
            messages.success(request, self.success_message)
        else:
            messages.error(request, f"Неверно заполнена форма: {groups_form.errors}")

        return redirect(reverse_lazy("tests_management:test_detail", args={self.test.id}))


class AddGroupsView(GroupsView):
    success_message = "Тест успешно назначен"
    
    def get_form(self):
        return forms.AddGroupsForm(self.test, data=self.request.POST)
    
    def do_action(self, groups_list):
        """
        Назначает тест выбранным группам и создает пустые TaskSolutions
        для выставления будущих оценок
        """
        
        self.test = self.get_object()
        
        with transaction.atomic():
            self.test.groups.add(*groups_list)
            
            blank_task_solutions = []
            for group in groups_list:
                for student in group.students.all():
                    for task in self.test.tasks.all():
                        blank_task_solutions.append(
                            TaskSolution(student=student, task=task)
                        )
                        
            TaskSolution.objects.bulk_create(blank_task_solutions)


class RemoveGroupsView(GroupsView):
    success_message = "Тест успешно отменен"
    
    def get_form(self):
        return forms.RemoveGroupsForm(self.test, data=self.request.POST)
    
    def do_action(self, groups_list):
        """
        Отменяет тест выбранным группам и удаляет
        связанные TaskSolutions
        """
        
        self.test = self.get_object()
        
        with transaction.atomic():
            self.test.groups.remove(*groups_list)
            
            if groups_list:
                TaskSolution.objects.filter(
                    student__group__in=groups_list,
                    task__test__id=self.test.id,
                ).delete()
