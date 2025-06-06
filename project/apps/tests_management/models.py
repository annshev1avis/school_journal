from django.db import models
from django.conf import settings

import apps.core.models
from apps.core.constants import STUDING_MONTHES_DICT


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
    month = models.SmallIntegerField(
        "месяц написания",
        choices=list(STUDING_MONTHES_DICT.items())
    )
    with_reflexive_level = models.BooleanField(
        "есть ли рефлексивный уровень",
        default=False,
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
    
    def save(self, *args, **kwargs):
        if self.id:
            self.with_reflexive_level = False
            for task in self.tasks.all():
                if task.level == Task.REFLEXIVE:
                    self.with_reflexive_level = True
                    break
        
        super().save(*args, **kwargs)
        
    def get_total_points(self, level):
        tasks = self.tasks.filter(level=level)
        return tasks.aggregate(sum_max_points=models.Sum("max_points"))["sum_max_points"]
    
    @property
    def total_basic_points(self):
        return self.get_total_points(Task.BASIC)
        
    @property
    def total_reflexive_points(self):
        return self.get_total_points(Task.REFLEXIVE)


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


class OrderedTasksManager(models.Manager):
    """
    Использование класса в качестве основного менеджера Task
    гарантирует сортировку по номеру (и уровню) заданий.
    Необходимо, чтобы во всех формах и таблицах-формах
    подписи соответствовали полям
    """
    def get_queryset(self):
        return super().get_queryset().order_by("num", "level")
    

class Task(models.Model):
    objects = OrderedTasksManager()
    
    BASIC = "Баз"
    REFLEXIVE = "Реф"
    TASK_LEVELS = {
        (BASIC, "Базовый"),
        (REFLEXIVE, "Рефлексивный")
    }
    
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        verbose_name="к какому тесту относится",
        related_name="tasks",
    )
    num = models.IntegerField(
        "номер задания в проверочной",
    )
    level = models.CharField(
        "уровень",
        max_length=3,
        choices=TASK_LEVELS,
        default=BASIC,
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
