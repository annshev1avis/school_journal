from django.db import models
from django.conf import settings
from django.urls import reverse

import apps.core.models


class Test(models.Model):
    name = models.CharField(
        "название",
        max_length=100,
    )
    subject = models.ForeignKey(
        apps.core.models.Subject,
        on_delete=models.PROTECT,
        verbose_name="предмет"
    )
    studing_year = models.IntegerField(
        "для какого класса",
        choices={
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
        },
    )
    last_update_date = models.DateTimeField(
        "время последнего редактирования",
        auto_now=True,
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="составитель",
        null=True,
    )
    groups = models.ManyToManyField(
        apps.core.models.Group,
        through="TestAssign",
        verbose_name="классы, которые будут писать эту проверочную",
        blank=True,
    )

    class Meta:
        verbose_name = "проверочная"
        verbose_name_plural = "проверочные"

    def __str__(self):
        return f"{self.name} {self.studing_year} класс"


class TestAssign(models.Model):
    group = models.ForeignKey(
        apps.core.models.Group,
        on_delete=models.CASCADE,
        verbose_name="класс, которому назначен тест",
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        verbose_name="тест",
    )
    writing_date = models.DateField(
        "дата написания",
        null=True,
    )

    class Meta:
        verbose_name = "планирование проверочной"
        verbose_name_plural = "планирование проверочных"

    def __str__(self):
        return f"{self.group} - {self.test}"


class Task(models.Model):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        verbose_name="к какому тесту относится",
        related_name="tasks",
    )
    num = models.IntegerField(
        "номер задания в проверочной",
    )
    sub_num = models.IntegerField(
        "подномер задания в проверочной",
        null=True,
        blank=True,
    )
    checked_skill = models.CharField(
        "проверяемый навык",
        max_length=300,
    )
    max_points = models.IntegerField(
        "максимальное количество баллов",
    )

    class Meta:
        verbose_name = "задание"
        verbose_name_plural = "задания"

    def __str__(self):
        return f"задание №{self.id}"
