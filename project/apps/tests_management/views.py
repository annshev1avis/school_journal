import random

from django.views import generic
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from apps.tests_management import forms
from apps.tests_management import models


class TestListView(generic.ListView):
    model = models.Test
    template_name = "tests_management/tests_list.html"
    context_object_name = "tests"


class TestWithTasksCreateView(generic.View):
    template_name = "tests_management/create_test.html"
    success_url = reverse_lazy("tests_management:tests_list")

    def get(self, request):
        test_form = forms.TestForm()
        task_formset = forms.TaskFormSet()

        context = {
            "uniq_stamp": random.random(),
            "test_form": test_form,
            "task_formset": task_formset,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        test_form = forms.TestForm(request.POST)
        if not test_form.is_valid():
            print(test_form.errors)
            return
        test = test_form.save()
        
        task_formset = forms.TaskFormSet(request.POST, instance=test)
        if not task_formset.is_valid():
            print(task_formset.errors)
            return
        task_formset.save()
        
        return redirect(self.success_url)
        