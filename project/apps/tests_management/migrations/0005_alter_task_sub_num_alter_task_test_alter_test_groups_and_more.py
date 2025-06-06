# Generated by Django 4.2.20 on 2025-05-04 10:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_alter_student_options_alter_subject_name"),
        ("tests_management", "0004_alter_test_creator_alter_testassign_writing_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="sub_num",
            field=models.IntegerField(
                blank=True, null=True, verbose_name="подномер задания в проверочной"
            ),
        ),
        migrations.AlterField(
            model_name="task",
            name="test",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tasks",
                to="tests_management.test",
                verbose_name="к какому тесту относится",
            ),
        ),
        migrations.AlterField(
            model_name="test",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                through="tests_management.TestAssign",
                to="core.group",
                verbose_name="классы, которые будут писать эту проверочную",
            ),
        ),
        migrations.AlterField(
            model_name="testassign",
            name="writing_date",
            field=models.DateField(
                blank=True, null=True, verbose_name="дата написания"
            ),
        ),
    ]
