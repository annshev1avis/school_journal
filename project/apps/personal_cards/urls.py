from django.urls import path

import apps.personal_cards.views as views


app_name = "personal_cards"
urlpatterns = [
    path("", views.CardsListView.as_view(), name="cards_list"),
    path(
        "<int:card_id>/", views.CardView.as_view(),
        name="card",
    ),
]
