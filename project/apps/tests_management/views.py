import random

from django.contrib import messages
from django.views import generic
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from apps.tests_management import forms
from apps.tests_management import models


# список тестов
class TestListView(generic.ListView):
    model = models.Test
    template_name = "tests_management/tests_list.html"
    context_object_name = "tests"


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


class TestWithTasksUpdateView(generic.View):
    template_name = "tests_management/update_test.html"
    
    def get(self, request, pk):
        test = get_object_or_404(models.Test, pk=pk)
        
        test_form = forms.TestForm(instance=test)
        tasks_formset = forms.TaskFormSet(instance=test, queryset=test.tasks)
    
        return render(
            request,
            self.template_name,
            {
                "test_pk": test.pk,
                "form": test_form,
                "tasks_formset": tasks_formset,
                "uniq_stamp": random.random()
            }
        )

    def post(self, request, pk):
        test = get_object_or_404(models.Test, pk=pk)
        
        test_form = forms.TestForm(request.POST, instance=test)
        tasks_formset = forms.TaskFormSet(request.POST, instance=test, queryset=test.tasks)
        
        if test_form.is_valid() and tasks_formset.is_valid():
            test = test_form.save()
            tasks_formset.save()
                
            messages.success(request, "Изменения сохранены")
            return redirect(reverse_lazy("tests_management:update_test", kwargs={"pk": test.pk}))
        
        messages.error(request, "Ошибки при заполнении формы")
        return render(
            request,
            self.template_name,
            {
                "test_pk": test.pk,
                "form": test_form,
                "tasks_formset": tasks_formset,
                "uniq_stamp": random.random()
            }
        )


class TestDeleteView(generic.DeleteView):
    model = models.Test
    template_name = "tests_management/test_confirm_delete.html"
    success_url = reverse_lazy("tests_management:tests_list")


# операции с отдельным заданием
class TaskCreateView(generic.CreateView):
    model = models.Task
    fields = ["num", "sub_num", "checked_skill", "max_points"]
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
