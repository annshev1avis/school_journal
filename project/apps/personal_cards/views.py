from django.shortcuts import render
from django.views import generic

import apps.core.models as core_models


class StudentsListView(generic.ListView):
    model = core_models.Student
    template_name = "personal_cards/students_list.html"
    context_object_name = "students"


class StudentCardView(generic.View):
    def get(self, request, student_id):
        pass
