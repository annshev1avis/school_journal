from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver

from apps.core.models import Group
from apps.tests_management.models import Test, Task
from apps.tests_app.models import TaskSolution


def generate_blank_solutions(task, group):
    print(task, group)
    solutions = []
    for student in group.students.all():
        solutions.append(
            TaskSolution(
                student=student,
                task=task,
            )
        )
    return solutions


@receiver(m2m_changed, sender=Test.groups.through)
def create_solutions_for_new_group(sender, instance, action, pk_set, **kwargs):
    """
    при назначении теста группе автоматически создает
    набор task_solution, в которые потом будут выставляться 
    результаты теста
    """
    if action == "post_add":
        blank_solutions = []
        
        for group in Group.objects.filter(pk__in=pk_set):
            for task in instance.tasks.all():
                blank_solutions.extend(
                    generate_blank_solutions(task, group),
                )
            
        TaskSolution.objects.bulk_create(blank_solutions)
        print("created:", blank_solutions)


@receiver(m2m_changed, sender=Test.groups.through)
def delete_solutions_of_group(sender, instance, action, pk_set, **kwargs):
    """
    при отмене назначения теста классу удаляет связанные 
    с тестом TaskSolutions
    """
    if action == "post_remove":
        for group in Group.objects.filter(pk__in=pk_set):
            print("deleted:", TaskSolution.objects.filter(student__group=group,
                task__test=instance,))
            TaskSolution.objects.filter(
                student__group=group,
                task__test=instance,
            ).delete()


@receiver(post_save, sender=Task)
def create_solutions_for_new_task(sender, instance, created, **kwargs):
    if created:
        blank_solutions = []
        for group in instance.test.groups.all():
            blank_solutions.extend(generate_blank_solutions(instance, group))
        
        print(blank_solutions)
        TaskSolution.objects.bulk_create(blank_solutions)
        print("created:", blank_solutions)
    
    
@receiver(post_delete, sender=Task)
def delete_solutions_of_task(sender, instance, **kwargs):
    print("deleted:", TaskSolution.objects.filter(task=instance))
    TaskSolution.objects.filter(task=instance).delete()
    