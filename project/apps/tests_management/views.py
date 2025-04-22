from django.views import generic
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from apps.tests_management import forms
from apps.tests_management import models


class TestListView(generic.ListView):
    model = models.Test
    template_name = "tests_management/tests_list.html"
    context_object_name = "tests"

    
class TestWithTasksCreateView(generic.CreateView):
    model = models.Test
    template_name = "tests_management/single_test.html"
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
        

class TestWithTasksUpdateView(generic.UpdateView):
    pass


class TestWithTasksDeleteView(generic.DeleteView):
    pass
