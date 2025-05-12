import django.forms
from django.shortcuts import render
from django.views import generic

from apps.core.models import Student, Group
from apps.core.views import ListFiltersMixin


class StudentsListView(ListFiltersMixin, generic.ListView):
    model = Student
    template_name = "personal_cards/students_list.html"
    context_object_name = "students"
    filter_fields = ["group"]


class StudentCardView(generic.View):
    template_name = "personal_card.html"
    def get(self, request, student_id):
        student = Student.objects.get(id=student_id)
        