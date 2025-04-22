from django.urls import path

from apps.tests_management import views


app_name = "tests_management"

urlpatterns = [
    path("", views.TestListView.as_view(), name="tests_list"),
    path("create_test/", views.TestWithTasksCreateView.as_view(), name="create_test"),
    path(
        "test/<int:pk>/",
        views.TestWithTasksUpdateView.as_view(),
        name="update_test",
    ),
]
