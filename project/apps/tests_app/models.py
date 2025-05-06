from django.db import models

import apps.core.models


class TaskSolution(models.Model):
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
