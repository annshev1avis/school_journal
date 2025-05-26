from django.db import models

import apps.core.models
from apps.tests_management.models import Task, Test


class OrderedTasksManager(models.Manager):
    """
    Использование класса в качестве основного менеджера TaskSolution
    гарантирует сортировку по номеру (и уровню) заданий.
    Необходимо, чтобы во всех формах и таблицах-формах
    подписи соответствовали полям
    """
    def get_queryset(self):
        return super().get_queryset().order_by("task__num", "task__level")


class TaskSolution(models.Model):
    objects = OrderedTasksManager()
    
    student = models.ForeignKey(
        apps.core.models.Student,
        on_delete=models.CASCADE,
        related_name="tasks_solutions",
        verbose_name="ученик",
    )
    task = models.ForeignKey(
        "tests_management.Task",
        on_delete=models.CASCADE,
        related_name="students",
        verbose_name="задание",
    )
    result = models.SmallIntegerField(
        "результат в баллах",
        null=True,
        blank=True,
        default=None,
    )

    class Meta:
        verbose_name = "решение"
        verbose_name_plural = "решения"


class TestSolutions:
    """
    Предоставляет удобный интерфейс для доступа к данным
    о результатах учеников по переданному тесту
    """
    def __init__(self, test):
        self.test = test
        self.solutions_queryset = (
            TaskSolution.objects
            .filter(task__test=self.test)
        )
        
    def get_student_solutions(self, student):
        return self.solutions_queryset.filter(student=student)
        
    def student_has_taken(self, student):
        for task in self.get_student_solutions(student):
            if task.result is None:
                return False
        return True
    
    def get_student_basic_total_score(self, student):
        return (
            self.get_student_solutions(student)
            .filter(task__level=Task.BASIC)
            .aggregate(total_score=models.Sum("result"))
            ["total_score"]
        )
    
    def get_student_reflexive_total_score(self, student):
        return (
            self.get_student_solutions(student)
            .filter(task__level=Task.REFLEXIVE)
            .aggregate(total_score=models.Sum("result"))
            ["total_score"]
        )
    
    def get_student_basic_percent(self, student):
        return (
            (self.get_student_basic_total_score(student) 
            / self.test.total_basic_points) * 100
        )
    
    def get_student_reflexive_percent(self, student):
        return (
            self.get_student_reflexive_total_score(student) 
            / self.test.total_reflexive_points * 100
        )


class TasksStatistics:
    """
    Предоставляет удобный интерфейс для доступа к данным
    об успешности решения заданий
    """
    def __init__(self, test):
        self.test = test
        self.solutions = TaskSolution.objects.filter(task__test=self.test)
        
    def get_count(self, task, success=True):
        filters = {"task": task}
        
        if success:
            filters["result__gt"] = 0
        else:
            filters["result"] = 0
            
        return (
            self.solutions.filter(**filters).aggregate(count=models.Count("*"))
        )["count"]
