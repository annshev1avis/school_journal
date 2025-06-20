from django.views.generic import TemplateView
from django.urls import path

from apps.tests_management import views


app_name = "tests_management"

urlpatterns = [
    path("", views.TestListView.as_view(), name="tests_list"),
    path("create_test/", views.TestCreateView.as_view(), name="create_test"),
    path(
        "test/<int:pk>/",
        views.TestDetailView.as_view(),
        name="test_detail",
    ),
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
        "test/<int:test_pk>/task/create/",
        views.TaskCreateView.as_view(),
        name="create_task",
    ),
    path(
        'publish_test/<int:pk>/',
        views.PublishTestView.as_view(),
        name='publish_test'
    ),
    path(
        "test/<int:pk>/add_groups/",
        views.AddGroupsView.as_view(),
        name="add_groups"
    ),
    path(
        "test/<int:pk>/remove_groups/",
        views.RemoveGroupsView.as_view(),
        name="remove_groups"
    ),
]
