from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from apps.core.models import Group
from apps.tests_management.models import Test
from apps.tests_app.models import TaskSolution


def generate_blank_task_solutions(test, group):
    task_solutions = []
    for student in group.students.all():
        for task in test.tasks.all():
            task_solutions.append(
                TaskSolution(
                    student=student,
                    task=task,
                )
            )
    return task_solutions


@receiver(m2m_changed, sender=Test.groups.through)
def create_related_task_solutions(sender, instance, action, pk_set, **kwargs):
    """
    при назначении теста группе автоматически создает
    набор task_solution, в которые потом будут выставляться 
    результаты теста
    """
    if action == "post_add":
        groups = [
            Group.objects.get(pk=group_id)
            for group_id in pk_set
        ]
        blank_task_solutions = []
        
        for group in groups:   
            blank_task_solutions.extend(
                generate_blank_task_solutions(instance, group),
            )
            
        TaskSolution.objects.bulk_create(blank_task_solutions)


@receiver(m2m_changed, sender=Test.groups.through)
def delete_related_task_solutions(sender, instance, action, pk_set, **kwargs):
    """
    при отмене назначения теста классу удаляет связанные 
    с тестом TaskSolutions
    """
    if action == "post_remove":
        groups = [
            Group.objects.get(pk=group_id)
            for group_id in pk_set
        ]
        for group in groups:
            TaskSolution.objects.filter(
                student__in=group.students.all(),
                task__in=instance.tasks.all(),
            ).delete()
