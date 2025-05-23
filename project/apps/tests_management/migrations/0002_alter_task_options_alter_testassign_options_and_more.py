# Generated by Django 4.2 on 2025-04-10 13:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
        ("tests_management", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="task",
            options={"verbose_name": "задание", "verbose_name_plural": "задания"},
        ),
        migrations.AlterModelOptions(
            name="testassign",
            options={
                "verbose_name": "планирование проверочной",
                "verbose_name_plural": "планирование проверочных",
            },
        ),
        migrations.AlterField(
            model_name="test",
            name="classes",
            field=models.ManyToManyField(
                through="tests_management.TestAssign",
                to="core.group",
                verbose_name="классы, которые будут писать эту проверочную",
            ),
        ),
        migrations.AlterField(
            model_name="test",
            name="subject",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="core.subject",
                verbose_name="предмет",
            ),
        ),
        migrations.AlterField(
            model_name="testassign",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="core.group",
                verbose_name="класс, которому назначен тест",
            ),
        ),
        migrations.DeleteModel(
            name="Subject",
        ),
    ]
