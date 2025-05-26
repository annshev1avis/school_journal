import datetime

from django.contrib import messages
import django.forms
from django.views import generic
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.urls import reverse_lazy

from apps.core.views import ListFiltersMixin
import apps.core.models as core_models
import apps.tests_app.forms as forms
import apps.tests_app.models as tests_app_models
import apps.tests_management.models as test_management_models


class TestAssignListView(ListFiltersMixin, generic.ListView):
    model = test_management_models.TestAssign
    template_name = "tests_app/test_assigns_list.html"
    context_object_name = "test_assigns"
    filter_fields = ["group"]


class MarksView(generic.View):
    """
    Выводит таблицу с учениками и выставленными баллами за задания в тесте.
    Учеников, которые не писали тест, выводит отдельным списком.
    Для удобного расчета итоговых столбцов 
    """
    def divide_students(self, students):
        """
        Во избежание ошибок отображения результатов в общей таблице,
        разделяет учеников, у которых выставлены все баллы и
        у которых есть None в результатах теста.
        """
        with_results = []
        without_results = []
        
        for student in students:
            task_solutions = (
                tests_app_models.TaskSolution
                .objects.filter(student=student, task__test=self.test)
            )
            if all(task.result is not None for task in task_solutions):
                with_results.append(student)
            else:
                without_results.append(student)
        
        return (with_results, without_results)
    
    def get_students_table_part(self, students):
        test_solutions = tests_app_models.TestSolutions(self.test)
        
        rows = []
        for student in students:
            row = {
                "name": f"{student.surname} {student.name}",
                "points": test_solutions.get_student_solutions(student),
                "basic_points": 
                    test_solutions.get_student_basic_total_score(student),
                "basic_percent": 
                    round(test_solutions.get_student_basic_percent(student)),
            }
            if self.test.with_reflexive_level:
                row.update({
                    "reflexive_points": 
                        test_solutions.get_student_reflexive_total_score(student),
                    "reflexive_percent": 
                        round(test_solutions.get_student_reflexive_percent(student)),
                })
            
            rows.append(row)
        
        return rows
    
    def get_statistics_table_part(self):
        tasks_statistics = tests_app_models.TasksStatistics(self.test)
        
        return {
            "success": [tasks_statistics.get_count(task, success=True) for task in self.tasks],
            "fail": [tasks_statistics.get_count(task, success=False) for task in self.tasks],
        }   
    
    def get(self, request, test_id, group_id):
        self.test = test_management_models.Test.objects.get(pk=test_id)
        self.tasks = test_management_models.Task.objects.filter(test_id=test_id)
        
        if len(self.tasks) == 0:
            return render(request, "tests_app/no_results.html", {})
        
        students_with_result, students_without_results = self.divide_students(
            core_models.Student.objects.filter(group_id=group_id)
            .order_by("surname", "name")
        )
        
        return render(
            request,
            "tests_app/view_marks.html",
            {
                "test": self.test,
                "group": core_models.Group.objects.get(pk=group_id),
                "tasks": self.tasks,
                "students_with_result": students_with_result,
                "students_without_results": students_without_results,
                "students_table_part": self.get_students_table_part(students_with_result),
                "statistic_table_part": self.get_statistics_table_part()
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
