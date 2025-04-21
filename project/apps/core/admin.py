from django.contrib import admin

import apps.core.models


admin.site.register(apps.core.models.Campus)
admin.site.register(apps.core.models.Group)
admin.site.register(apps.core.models.Student)
admin.site.register(apps.core.models.Subject)
