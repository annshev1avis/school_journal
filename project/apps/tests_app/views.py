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
from apps.tests_app.models import ResultsCalculator, TaskSolution, TasksStatistics
from apps.tests_management.models import TestAssign, Task, Test


class TestAssignListView(ListFiltersMixin, generic.ListView):
    model = TestAssign
    queryset = TestAssign.objects.filter(test__is_published=True)
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
                TaskSolution
                .objects.filter(student=student, task__test=self.test)
            )
            if all(task.result is not None for task in task_solutions):
                with_results.append(student)
            else:
                without_results.append(student)
        
        return (with_results, without_results)
    
    def get_students_table_part(self, students):  
        rows = []
        for student in students:
            calculator = ResultsCalculator(self.test, student)
            row = {
                "name": f"{student.surname} {student.name}",
                "points": calculator.get_solutions(),
                "basic_points": calculator.get_total_points(Task.BASIC),
                "basic_percent": 
                    round(calculator.get_total_percent(Task.BASIC)),
            }
            if self.test.with_reflexive_level:
                row.update({
                    "reflexive_points": 
                        calculator.get_total_points(Task.REFLEXIVE),
                    "reflexive_percent": 
                        round(calculator.get_total_percent(Task.REFLEXIVE)),
                })
            
            rows.append(row)
        
        return rows
    
    def get_statistics_table_part(self):
        tasks_statistics = TasksStatistics(self.test)
        
        return {
            "success": [tasks_statistics.get_count(task, success=True) for task in self.tasks],
            "fail": [tasks_statistics.get_count(task, success=False) for task in self.tasks],
        }   
    
    def get(self, request, test_id, group_id):
        self.test = Test.objects.get(pk=test_id)
        self.tasks = Task.objects.filter(test_id=test_id)
        
        if not self.test.is_published:
            return render(request, "tests_management/test_is_not_published.html", {})
        
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
            TaskSolution.objects
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
    
    def dispatch(self, request, *args, **kwargs):
        self.test_assign = TestAssign.objects.get(
            test_id=kwargs["test_id"],
            group_id=kwargs["group_id"]
        )
        
        if not self.test_assign.test.is_published:
            return redirect(reverse_lazy("tests_management:test_is_not_published"))
        
        self.students = (
            core_models.Student.objects
            .filter(group=self.test_assign.group)
            .order_by("surname", "name")
        )
        self.tasks = (
            Task.objects
            .filter(test=self.test_assign.test)
        )
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, test_id, group_id):
        return render(
            request,
            self.template_name,
            {
                "test": self.test_assign.test,
                "group": self.test_assign.group,
                "tasks": self.tasks,
                "students": self.students,
                "test_assign_form": forms.TestAssignForm(instance=self.test_assign),
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
        test_assign_form = forms.TestAssignForm(instance=self.test_assign, data=request.POST)
        student_formsets = self.get_student_solutions_formsets()
        
        
        if not test_assign_form.is_valid():
            return self.get(request, test_id, group_id)
        test_assign_form.save()
        
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
