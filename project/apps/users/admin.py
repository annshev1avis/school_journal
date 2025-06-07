from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

import apps.users.models


admin.site.register(apps.users.models.CustomUser, UserAdmin)
