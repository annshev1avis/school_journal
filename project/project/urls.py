from django.contrib import admin
from django.urls import include, path

import project.settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tests/", include("apps.tests_app.urls")),
    path("tests_management/", include("apps.tests_management.urls")),
] 

if project.settings.DEBUG:
    urlpatterns += (
        path(
            "__debug__/",
            include("debug_toolbar.urls"),
        ),
    )
