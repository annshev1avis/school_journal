from django.urls import path

import apps.tests_app.views as views


app_name = "tests_app"

urlpatterns = [
    path(
        "<int:test_id>/group/<int:group_id>/",
        views.SetMarksView.as_view(),
        name="set_marks",
    ),
]
