from django.db import models


class Group(models.Model):
    studing_year = models.IntegerField(
        "текущий год обучения",
        choices={
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
        },
    )
    letter = models.CharField(
        "буква класса",
        max_length=1,
    )
    year_created = models.PositiveSmallIntegerField(
        "в каком календарном году был создан класс"
    )
    is_active = models.BooleanField(
        "используется ли класс в текущем учебном году",
        default=True,
    )


class Student(models.Model):
    surname = models.CharField(
        "фамилия",
        max_length=20,
    )
    name = models.CharField(
        "имя",
        max_length=20,
    )
    patronomic = models.CharField(
        "отчество",
        max_length=20,
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name="students",
        verbose_name="класс",
    )
    tests = models.ManyToManyField(
        "tests_management.Test",
        related_name="students",
        verbose_name="решенные проверочные",
    )
    tasks = models.ManyToManyField(
        "tests_management.Task",
        through="TaskSolution",
        verbose_name="решенные задания",
    )


class TaskSolution(models.Model):
    student = models.ForeignKey(
        Student,
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
    )
