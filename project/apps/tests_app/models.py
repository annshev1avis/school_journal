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


class ResultsCalculator:
    """
    Предоставляет набор методов для расчета результатов теста
    """
    def __init__(self, test, student):
        self.test = test
        self.student = student
    
    def get_solutions(self):
        return TaskSolution.objects.filter(
            task__test=self.test,
            student=self.student,
            result__isnull=False
        )
        
    @property
    def empty_result(self):
        return len(self.get_solutions()) == 0
        
    def get_total_points(self, level):
        return (
            self.get_solutions()
            .filter(task__level=level)
            .aggregate(models.Sum("result"))["result__sum"]
        )

    def get_total_percent(self, level):
        return (
            (self.get_total_points(level) /
            self.test.get_total_points(level)) * 100
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
