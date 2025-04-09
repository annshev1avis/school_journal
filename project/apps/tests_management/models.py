from django.db import models
from django.conf import settings


class Subject(models.Model):
    name = models.CharField(max_length=30)


class Test(models.Model):
    name = models.CharField(
        "название",
        max_length=100,
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, verbose_name="предмет"
    )
    studing_year = models.IntegerField(
        "год обучения",
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
        on_delete=models.PROTECT,
        verbose_name="составитель",
    )
    classes = models.ManyToManyField(
        "tests_app.Group",
        through="TestAssign",
        verbose_name="классы, которые будут писать эту проверочную",
    )

    class Meta:
        verbose_name = "проверочная"
        verbose_name_plural = "проверочные"


class TestAssign(models.Model):
    group = models.ForeignKey(
        "tests_app.Group",
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
    )


class Task(models.Model):
    test = models.ForeignKey(
        Test,
        on_delete=models.PROTECT,
        verbose_name="к какому тесту относится",
    )
    num = models.IntegerField(
        "номер задания в проверочной",
    )
    sub_num = models.IntegerField(
        "подномер задания в проверочной",
        null=True,
    )
    checked_skill = models.CharField(
        "проверяемый навык",
        max_length=300,
    )
    max_points = models.IntegerField(
        "максимальное количество баллов",
    )
