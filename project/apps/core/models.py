from django.db import models


class Campus(models.Model):
    name = models.CharField(
        "название",
        max_length=30,
    )

    class Meta:
        verbose_name = "кампус"
        verbose_name_plural = "кампусы"
    
    def __str__(self):
        return self.name


class Group(models.Model):
    campus = models.ForeignKey(
        Campus,
        on_delete=models.CASCADE,
        verbose_name="кампус, которому принадлежит класс",
    )
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

    class Meta:
        verbose_name = "класс"
        verbose_name_plural = "классы"

    def __str__(self):
        return f"{self.studing_year} {self.letter} - {self.campus.name}"


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

    class Meta:
        verbose_name = "ученик"
        verbose_name_plural = "ученики"

    def __str__(self):
        return f"{self.surname} {self.name} {self.group}"


class Subject(models.Model):
    name = models.CharField(
        "название",
        max_length=30,
    )

    class Meta:
        verbose_name = "предмет"
        verbose_name_plural = "предметы"

    def __str__(self):
        return self.name
