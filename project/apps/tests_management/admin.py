from django.contrib import admin

import apps.tests_management.models


admin.site.register(apps.tests_management.models.Task)
admin.site.register(apps.tests_management.models.Test)
admin.site.register(apps.tests_management.models.TestAssign)
