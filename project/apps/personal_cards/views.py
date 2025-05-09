from django.shortcuts import render
from django.views import generic

from apps.core.models import Student
from apps.personal_cards import forms


class StudentsListView(generic.ListView):
    model = Student
    template_name = "personal_cards/students_list.html"
    context_object_name = "students"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filters_form"] = forms.FiltersForm()
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # фильтрация по классу
        group_id = self.request.GET.get("group")
        if group_id:
            group_id = int(group_id)
            queryset = queryset.filter(group_id=group_id)
            
        return queryset


class StudentCardView(generic.View):
    template_name = "personal_card.html"
    def get(self, request, student_id):
        student = Student.objects.get(id=student_id)
        
        
