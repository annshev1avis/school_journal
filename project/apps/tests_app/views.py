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


class StudentTestResults:
    """
    Представляет результаты выполнения теста для группы студентов.
    Вычисляет итоговые показатели:
    - сумма баллов по каждому студенту
    - процент выполнения теста
    - статистику по решению каждого задания
    """
    def __init__(self, students, tasks):
        self.students = students
        self.tasks = tasks
        self.max_test_score = (
            self.tasks.aggregate(
                total_max_points=Sum("max_points")
            )["total_max_points"]
        )
        
        self.student_task_scores = self._get_student_task_scores()
        self.student_total_scores = self._get_student_total_scores()
        self.student_percentage_scores = self._get_student_percentage_scores()
        self.task_success_counts = self._get_task_success_counts()
        self.task_failure_counts = self._get_task_failure_counts()

    def _get_student_task_scores(self):
        """
        Возвращает словарь с баллами каждого студента по всем заданиям
        {student: {task: score}}
        """
        return {
            student: {
                task: tests_app_models.TaskSolution
                .objects.get(student=student, task=task).result
                for task in self.tasks
            }
            for student in self.students
        }

    def _get_student_total_scores(self):
        """
        Возвращает суммарные баллы каждого студента по всем заданиям
        {student: total_score}
        """
        return {
            student: sum(scores.values())
            for student, scores in self.student_task_scores.items()
        }

    def _get_student_percentage_scores(self):
        """
        Возвращает процент выполнения теста для каждого студента
        {student: percentage_score}
        """
        return {
            student: total_score / self.max_test_score * 100
            for student, total_score in self.student_total_scores.items()
        }

    def _get_task_success_counts(self):
        """
        Возвращает количество студентов, успешно решивших задание
        {task: success_count}
        """
        return {
            task: sum(
                score > 0 for score in [
                    self.student_task_scores[student][task] 
                    for student in self.students
                ]
            )
            for task in self.tasks
        }
        
    def _get_task_failure_counts(self):
        """
        Возвращает количество студентов, не решивших задание
        {task: failure_count}
        """
        return {
            task: sum(
                score == 0 for score in [
                    self.student_task_scores[student][task] 
                    for student in self.students
                ]
            )
            for task in self.tasks
        }


class MarksView(generic.View):
    """
    Выводит таблицу с учениками и выставленными баллами за задания в тесте.
    Учеников, которые не писали тест, выводит отдельным списком.
    Для удобного расчета итоговых столбцов данные загружаются в 
    экземпляр ResultsDicts
    """
    def divide_students(self):
        """
        Во избежание ошибок отображения результатов в общей таблице
        разделяет учеников, у которых выставлены все баллы и
        у которых есть None в результатах теста.
        """
        with_results = []
        without_results = []
        
        for student in self.students:
            task_solutions = (
                tests_app_models.TaskSolution
                .objects.filter(student=student, task__in=self.tasks)
            )
            if all(task.result is not None for task in task_solutions):
                with_results.append(student)
            else:
                without_results.append(student)
        
        return (with_results, without_results)
    
    def get(self, request, test_id, group_id):
        self.students = (
            core_models.Student.objects.filter(group_id=group_id)
            .order_by("surname", "name")
        )
        self.tasks = (
            test_management_models.Task.objects
            .filter(test_id=test_id)
            .order_by("num", "sub_num")
        )
        
        students_with_result, students_without_results = (
            self.divide_students()
        )
        results = StudentTestResults(
            students_with_result,
            self.tasks,
        )
        
        return render(
            request,
            "tests_app/view_marks.html",
            {
                "test": test_management_models.Test.objects.get(pk=test_id),
                "group": core_models.Group.objects.get(pk=group_id),
                "tasks": self.tasks,
                "results": results,
                "students_without_results": students_without_results
            }
        )


class SetMarksView(generic.View):
    """
    View с таблицей для выставления оценок за 
    определенную проверочную определенному классу
    """
    template_name = "tests_app/set_marks.html"
    
    def get_task_solutions(self, student):
        """
        Возвращает TaskSolutions ученика student,
        связанные с этим тестом
        """
        return(
            tests_app_models.TaskSolution.objects
            .filter(
                student=student,
                task__in=self.tasks,
            )
            .order_by("task__num", "task__sub_num")
        )
    
    def get_student_solutions_formsets(self):
        """
        Возвращает словарь вида ученик: 
        формсет для выставления TaskSolution связанных с этим тестом.
        Обновляет данными из request.POST, если они есть
        """
        return {
            student: forms.StudentTestSolutionFormSet(
                self.request.POST if self.request.POST else None,
                queryset=self.get_task_solutions(student),
                prefix=f"student-id-{student.id}"
            )
            for student in self.students
        }
    
    def get(self, request, test_id, group_id):
        self.students = (
            core_models.Student.objects.filter(group_id=group_id)
            .order_by("surname", "name")
        )
        self.tasks = (
            test_management_models.Task.objects
            .filter(test_id=test_id)
            .order_by("num", "sub_num")
        )
        
        return render(
            request,
            self.template_name,
            {
                "test": test_management_models.Test.objects.get(pk=test_id),
                "group": core_models.Group.objects.get(pk=group_id),
                "tasks": self.tasks,
                "students": self.students,
                "student_solutions_formsets":
                    self.get_student_solutions_formsets(),
            },
        )
        
    def send_formset_errors_message(self, formset):
        student = formset[0].instance.student
        error_messages_str = (
            ''.join(error.message for error in formset.non_form_errors().data)
        )
        messages.error(
            self.request,
            f"Ошибка при заполнении '{student.surname} {student.name}': "
            f"{error_messages_str}"
        )
        
    def post(self, request, test_id, group_id):
        self.students = core_models.Student.objects.filter(group_id=group_id)
        self.tasks = (
            test_management_models.Task.objects
            .filter(test_id=test_id)
            .order_by("num", "sub_num")
        )
        
        student_formsets = self.get_student_solutions_formsets()
        for student, formset in student_formsets.items():
            if not formset.is_valid():
                self.send_formset_errors_message(formset)
                return self.get(request, test_id, group_id)
            
            formset.save()                
                
        return redirect(
            reverse_lazy(
                "tests_app:view_marks",
                kwargs={"test_id": test_id, "group_id": group_id},
            )
        )
        