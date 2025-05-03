from django.urls import path

from apps.tests_management import views


app_name = "tests_management"

urlpatterns = [
    path("", views.TestListView.as_view(), name="tests_list"),
    path("create_test/", views.TestWithTasksCreateView.as_view(), name="create_test"),
    path(
        "test/<int:pk>/update/",
        views.TestWithTasksUpdateView.as_view(),
        name="update_test",
    ),
    path(
        "test/<int:pk>/delete/",
        views.TestDeleteView.as_view(),
        name="delete_test",
    ),
    path(
        "task/<int:pk>/update/",
        views.TaskUpdateView.as_view(),
        name="update_task",
    ),
    path(
        "task/<int:pk>/delete/",
        views.TaskDeleteView.as_view(),
        name="delete_task",
    ),
]
