from django.urls import path

import apps.personal_cards.views as views


app_name = "personal_cards"
urlpatterns = [
    path("", views.GroupsListView.as_view(), name="groups_list"),
    path("groups/<int:group_id>/", views.GroupActiveCardsView.as_view(), name="group"),
    path(
        "<int:group_id>/archived/", views.GroupArchivedCardsView.as_view(),
        name="group_archived"
    ),
    path(
        "cards/<int:card_id>/", views.CardView.as_view(),
        name="card",
    ),
    path(
        "groups/<int:pk>/create_cards/",
        views.CreateCardsView.as_view(),
        name="create_cards"
    )
]
