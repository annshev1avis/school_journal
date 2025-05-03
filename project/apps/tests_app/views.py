import datetime

from django.views.generic import View
from django.shortcuts import render

from apps.core.models import Student
import apps.tests_app.forms as forms
from apps.tests_app.models import TaskSolution
from apps.tests_management.models import Task


class SetMarksView(View):
    template_name = "tests/test_form.html"
    def get(self, request, test_id, group_id):
        tasks = Task.objects.filter(test_id=test_id).order_by("num", "sub_num")
        students = Student.objects.filter(group_id=group_id)
        
        tasks_structure = {}
        for task in tasks:
            if task.num in tasks_structure:
                tasks_structure[task.num].append(task.sub_num)
            else:
                tasks_structure[task.num] = [task.sub_num]
        
        
        return render(
            request,
            self.template_name,
            {
                "tasks": tasks,
                "students": students,
                "tasks_structure": tasks_structure,
            },
        )
        