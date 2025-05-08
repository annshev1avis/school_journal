from django.urls import path

import apps.personal_cards.views as views


app_name = "personal_cards"
urlpatterns = [
    path("", views.StudentsListView.as_view(), name="students_list"),
    path(
        "<int:student_id>/", views.StudentCardView.as_view(),
        name="student_card",
    ),
]
