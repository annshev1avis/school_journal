from django.contrib import admin

import apps.users.models


admin.site.register(apps.users.models.CustomUser)
