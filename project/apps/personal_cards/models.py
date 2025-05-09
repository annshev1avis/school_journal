from django.db import models

from apps.core.models import Student, Subject


class PersonalMonthCard(models.Model):
    """
    Ежемесячный личный отчет об успеваемости ученика
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="personal_cards",
        verbose_name="ученик"
    )
    start_date = models.DateField(
        "начало отчётного периода",
    )
    end_date = models.DateField(
        "конец отчётного периода",
    )
    is_archived = models.BooleanField(
        "является архивной записью",
        default=False,
    )
    
    class Meta:
        verbose_name = "Личная карточка"
        verbose_name_plural = "Личные карточки"
    

class PersonalRecommendations(models.Model):
    """
    Персональные рекомендации для улучшения образовательных
    результатов по какому-то предмету. Заполняются вручную
    преподавателем.
    """
    personal_card = models.ForeignKey(
        PersonalMonthCard,
        on_delete=models.CASCADE,
        related_name="recommendations",
        verbose_name="к какой карточке относится",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        verbose_name="к какому предмету относится",
    )
    text = models.TextField(
        "текст",
        null=True,
        blank=True,
    )
    
    class Meta:
        verbose_name = "Персональная рекомендация"
        verbose_name_plural = "Персональные рекомендации"


class PersonalStrength(models.Model):
    """
    Проявленные учеником успехи
    по какому-то предмету. Заполняются вручную
    преподавателем.
    """
    personal_card = models.ForeignKey(
        PersonalMonthCard,
        on_delete=models.CASCADE,
        related_name="strengths",
        verbose_name="к какой карточке относится",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        verbose_name="к какому предмету относится",
    )
    text = models.TextField(
        "текст",
        null=True,
        blank=True,
    )
    
    class Meta:
        verbose_name = "Заметка о проявленных успехах"
        verbose_name_plural = "Проявленные успехи"


class SoftSkill(models.Model):
    """
    Межпредметный навык
    """
    name = models.CharField(
        "название",
        max_length=50,
    )
    
    class Meta:
        verbose_name = "Межпредметный навык"
        verbose_name_plural = "Межпредметные навыки"
    

class SoftSkillMark(models.Model):
    """
    Оценка межпредметного навыка. Выставляется педагогом
    в рамках составления личных отчетов
    """
    card = models.ForeignKey(
        PersonalMonthCard,
        on_delete=models.CASCADE,
        verbose_name="к какой карточке относится"
    )
    skill = models.ForeignKey(
        SoftSkill,
        on_delete=models.CASCADE,
        verbose_name="к какому навыку относится",
    )
    
    MARKS_CHOICES = [
        ("Нет", "Нет"),
        ("Скорее нет", "Скорее нет"),
        ("Скорее да", "Скорее да"),
        ("Да", "Да"),
    ]
    mark = models.CharField(
        "оценка",
        max_length=10,
        choices=MARKS_CHOICES,
        null=True,
        blank=True,
    )
    
    class Meta:
        verbose_name = "Оценка межпредметного навыка"
        verbose_name_plural = "Оценки межпредметных навыков"
