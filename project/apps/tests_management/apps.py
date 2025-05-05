from django.apps import AppConfig


class TestsManagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tests_management"
    verbose_name = "Управление проверочными"
    
    def ready(self):
        from apps.tests_management import signals
        return super().ready()
