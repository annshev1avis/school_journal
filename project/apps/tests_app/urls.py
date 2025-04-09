from django.urls import path

import apps.tests_app.views


app_name = "tests"

urlpatterns = [
    path("", apps.tests_app.views.show_test_page, name="main_page"),
]
