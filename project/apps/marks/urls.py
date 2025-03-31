from django.urls import path

import apps.marks.views


app_name = "marks"

urlpatterns = [
   path("", apps.marks.views.show_test_page, name="main_page"),
]
