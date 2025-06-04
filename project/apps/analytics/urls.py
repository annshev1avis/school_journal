from django.urls import path

import apps.analytics.views as views

app_name = "analytics"
urlpatterns = [
    path("", views.ChooseSectionView.as_view(), name="choose_section"),
    path("tests/", views.TestsListView.as_view(), name="tests_list"),
    path("tests/<int:pk>/", views.TestDetailView.as_view(), name="test"),
    path("groups/", views.GroupsListView.as_view(), name="groups_list"),
    path("groups/<int:pk>/", views.GroupDetailView.as_view(), name="group"),
]
