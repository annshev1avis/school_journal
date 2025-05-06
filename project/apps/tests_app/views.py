import datetime

from django.contrib import messages
from django.views import generic
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.urls import reverse_lazy

import apps.core.models as core_models
import apps.tests_app.forms as forms
import apps.tests_app.models as tests_app_models
import apps.tests_management.models as test_management_models


class TestAssignListView(generic.ListView):
    model = test_management_models.TestAssign
    template_name = "tests_app/test_assigns_list.html"
    context_object_name = "test_assigns"


class ResultsMatrix:
    def __init__(self, students, tasks, test_max_points):
        self.students = students
        self.tasks = tasks
        self.test_max_points = test_max_points
        
        self.points = self.get_points()
        self.result_in_points = self.get_result_in_points()
        self.result_in_percents = self.get_result_in_percents()
        self.task_solved_amount = self.get_task_solved_amount()
        self.task_unsolved_amount = self.get_task_unsolved_amount()

    def get_points(self):
        """
        возвращает словарь, который хранит
        для каждого ученика словарь с полученными 
        за каждое задание баллами (баллы в виде int)
        """
        return {
            student: {
                task: tests_app_models.TaskSolution
                .objects.get(student=student, task=task).result
                for task in self.tasks
            }
            for student in self.students
        }

    def get_result_in_points(self):
        """
        сумма баллов для каждого ученика
        """
        return {
            student: sum(points.values())
            for student, points in self.points.items()
        }

    def get_result_in_percents(self):
        """
        процент выполнения теста для каждого ученика
        """
        return {
            student: total_points / self.test_max_points * 100
            for student, total_points in self.result_in_points.items()
        }

    def get_task_solved_amount(self):
        """
        количество учеников, решивших задание для каждого задания
        """
        return {
            task: sum(
                [int(self.points[student][task] > 0) for student in self.students]
            )
            for task in self.tasks
        }
        
    def get_task_unsolved_amount(self):
        """
        количество учеников, не решивших задание для каждого задания
        """
        return {
            task: sum(
                [int(self.points[student][task] == 0) for student in self.students]
            )
            for task in self.tasks
        }
        

class MarksView(generic.View):
    def divide_students(self, students, tasks):
        """
        Во избежание ошибок отображения результатов в общей таблице
        разделяет учеников, у которых выставлены все баллы и
        у которых есть None в результатах теста.
        """
        with_results = []
        without_results = []
        
        for student in students:
            task_solutions = (
                tests_app_models.TaskSolution
                .objects.filter(student=student, task__in=tasks)
            )
            if all(task.result is not None for task in task_solutions):
                with_results.append(student)
            else:
                without_results.append(student)
        
        return (with_results, without_results)
    
    def get(self, request, test_id, group_id):
        students = (
            core_models.Student.objects.filter(group_id=group_id)
            .order_by("surname", "name")
        )
        tasks = (
            test_management_models.Task.objects
            .filter(test_id=test_id)
            .order_by("num", "sub_num")
        )
        
        students_with_result, students_without_results = (
            self.divide_students(students, tasks)
        )
        test_max_points = tasks.aggregate(total_max_points=Sum("max_points"))["total_max_points"]
        
        results_matrix = ResultsMatrix(
            students_with_result,
            tasks,
            test_max_points,
        )
        
        return render(
            request,
            "tests_app/view_marks.html",
            {
                "test": test_management_models.Test.objects.get(pk=test_id),
                "group": core_models.Group.objects.get(pk=group_id),
                "tasks": tasks,
                "results_matrix": results_matrix,
                "students_without_results": students_without_results
            }
        )


class SetMarksView(generic.View):
    template_name = "tests_app/set_marks.html"
    
    def get(self, request, test_id, group_id):
        test = test_management_models.Test.objects.get(pk=test_id)
        group = core_models.Group.objects.get(pk=group_id)
        students = (
            core_models.Student.objects.filter(group_id=group_id)
            .order_by("surname", "name")
        )
        tasks = (
            test_management_models.Task.objects
            .filter(test_id=test_id)
            .order_by("num", "sub_num")
        )
    
        student_solutions_formsets = {}
        for student in students:
            student_solutions_formsets[student] = forms.StudentTestSolutionFormSet(
                queryset=(
                    tests_app_models.TaskSolution.objects
                    .filter(
                        student=student,
                        task__in=tasks,
                    )
                    .order_by("task__num", "task__sub_num")
                ),
                prefix=f"student-id-{student.id}"
            )
        
        return render(
            request,
            self.template_name,
            {
                "test": test,
                "group": group,
                "tasks": tasks,
                "students": students,
                "student_solutions_formsets":
                    student_solutions_formsets,
            },
        )
        
    def post(self, request, test_id, group_id):
        students = core_models.Student.objects.filter(group_id=group_id)
        tasks = (
            test_management_models.Task.objects
            .filter(test_id=test_id)
            .order_by("num", "sub_num")
        )
        student_formsets = [
            forms.StudentTestSolutionFormSet(
                request.POST,
                queryset=(
                    tests_app_models.TaskSolution.objects
                    .filter(
                        student=student,
                        task__in=tasks,
                    )
                ),
                prefix=f"student-id-{student.id}"
            ) for student in students
        ]
        
        for formset in student_formsets:
            if not formset.is_valid():
                student = formset[0].instance.student
                error_messages_str = (
                    ''.join(error.message for error in formset.non_form_errors().data)
                )
                messages.error(
                    request,
                    f"Ошибка при заполнении '{student.surname} {student.name}': "
                    f"{error_messages_str}"
                )
                return self.get(request, test_id, group_id)
            formset.save()                
                
        return redirect(
            reverse_lazy(
                "tests_app:view_marks",
                kwargs={"test_id": test_id, "group_id": group_id},
            )
        )
        