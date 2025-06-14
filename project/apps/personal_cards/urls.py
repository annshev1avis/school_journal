from django.urls import path

import apps.personal_cards.views as views


app_name = "personal_cards"
urlpatterns = [
    path("", views.GroupsListView.as_view(), name="groups_list"),
    path("groups/<int:group_id>/", views.GroupBatchesListView.as_view(), name="group"),
    # действия с папкой карточек
    path(
        "batch/<int:pk>/", views.BatchView.as_view(),
        name="batch",
    ),
    path(
        "batch/<int:pk>/delete/",
        views.DeleteBatchView.as_view(),
        name="delete_batch"
    ),
    path(
        "groups/<int:pk>/create_cards/",
        views.CreateBatchWithCardsView.as_view(),
        name="create_batch"
    ),
    # действия с карточкой
    path(
        "cards/<int:card_id>/", views.CardView.as_view(),
        name="card",
    ),
]
