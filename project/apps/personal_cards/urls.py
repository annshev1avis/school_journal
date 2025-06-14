from django.urls import path

import apps.personal_cards.views as views


app_name = "personal_cards"
urlpatterns = [
    path("", views.GroupsListView.as_view(), name="groups_list"),
    path("groups/<int:group_id>/", views.GroupBatchesListView.as_view(), name="group"),
    # действия с папкой карточек
    path(
        "batches/<int:pk>/", views.BatchView.as_view(),
        name="batch",
    ),
    path(
        "batches/<int:pk>/delete/",
        views.DeleteBatchView.as_view(),
        name="delete_batch"
    ),
    path(
        "groups/<int:pk>/create_cards/",
        views.CreateBatchWithCardsView.as_view(),
        name="create_batch"
    ),
    path(
        "batches/<int:pk>/pdf/", views.DownloadBatchCards.as_view(),
        name="download_batch_cards",
    ),
    # действия с карточкой
    path(
        "cards/<int:card_id>/", views.CardView.as_view(),
        name="card",
    ),
    path(
        "cards/<int:pk>/pdf/", views.DownloadCardView.as_view(),
        name="download_card",
    ),
]
