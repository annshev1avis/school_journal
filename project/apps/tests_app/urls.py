from django.urls import path

import apps.tests_app.views as views


app_name = "tests_app"

urlpatterns = [
    path("", views.TestAssignListView.as_view(), name="test_assigns_list"),
    path(
        "<int:test_id>/groups/<int:group_id>/",
        views.MarksView.as_view(),
        name="view_marks",
    ),
    path(
        "<int:test_id>/groups/<int:group_id>/set_marks",
        views.SetMarksView.as_view(),
        name="set_marks",
    ),
]
