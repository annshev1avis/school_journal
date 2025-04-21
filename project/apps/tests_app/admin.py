from django.contrib import admin

import apps.tests_app.models


admin.site.register(apps.tests_app.models.TaskSolution)
