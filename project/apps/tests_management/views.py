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
class TestWithTasksCreateView(generic.CreateView):
    model = models.Test
    template_name = "tests_management/test_form.html"
    form_class = forms.TestForm
    success_url = reverse_lazy("tests_management:tests_list")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task_formset"] = self.get_task_formset()
        return context
    
    def get_task_formset(self):
        return forms.TaskFormSet(
            self.request.POST 
            if self.request.POST
            else None
        )
    
    def form_valid(self, form, task_formset):
        response = super().form_valid(form)
        
        test = self.object
        task_formset.instance = test
        task_formset.save()
        
        return response

    def post(self, request, *args, **kwargs):
        self.object = None
        
        test_form = self.get_form()
        task_formset = self.get_task_formset()
        
        if test_form.is_valid() and task_formset.is_valid():
            return self.form_valid(test_form, task_formset)
        else:
            return self.form_invalid(test_form)
        

class TestWithTasksUpdateView(generic.View):
    template_name = "tests_management/test_form.html"
    
    def get(self, request, pk):
        test = get_object_or_404(models.Test, pk=pk)
        
        test_form = forms.TestForm(instance=test)
        task_formset = forms.TaskFormSet(instance=test)
    
        return render(
            request,
            self.template_name,
            {
                "form": test_form,
                "task_formset": task_formset,
                "uniq_stamp": random.random()
            }
        )

    def post(self, request, pk):
        test = get_object_or_404(models.Test, pk=pk)
        
        test_form = forms.TestForm(request.POST, instance=test)
        task_formset = forms.TaskFormSet(request.POST, instance=test)
        
        if test_form.is_valid() and task_formset.is_valid():
            test = test_form.save()
            task_formset.save()
                
            messages.success(request, "Изменения сохранены")
            return redirect(reverse_lazy("tests_management:tests_list"))
        
        messages.error(request, "Ошибки при заполнении формы")
        return render(
            request,
            self.template_name,
            {
                "form": test_form,
                "task_formset": task_formset,
                "uniq_stamp": random.random()
            }
        )


class TestDeleteView(generic.DeleteView):
    model = models.Test
    template_name = "test_confirm_delete.html"
    success_url = reverse_lazy("tests_app:tests_list")


# операции с отдельным заданием
class TaskUpdateView(generic.UpdateView):
    model = models.Task
    fields = ["num", "sub_num", "checked_skill", "max_points"]
    template_name = "tests_management/task_form.html"
    success_url = reverse_lazy("tests_management:update_test")


class TaskDeleteView(generic.DeleteView):
    model = models.Task
    template_name = "task_confirm_delete.html"
    success_url = reverse_lazy("tests_management:update_test")
