from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse_lazy

import apps.personal_cards.forms as forms
import apps.personal_cards.models as models
from apps.core.views import ListFiltersMixin


class CardsListView(ListFiltersMixin, generic.ListView):
    model = models.PersonalMonthCard
    template_name = "personal_cards/cards_list.html"
    context_object_name = "cards"
    # filter_fields = ["group"]


class CardView(generic.View):
    template_name = "personal_card.html"
    
    def dispatch(self, request, *args, **kwargs):
        self.card = models.PersonalMonthCard.objects.get(
            id=kwargs["card_id"]
        )
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, card_id):
        return render(
            request,
            "personal_cards/personal_card.html",
            {
                "card": self.card,
                "recommendations_formset": self.get_recommendations_formset(),
                "strengths_formset": self.get_strengths_formset(), 
            },
        )

    def get_recommendations_formset(self):
        return forms.RecommendationsFormset(
            self.request.POST if self.request.POST else None,
            instance=self.card,
        )
        
    def get_strengths_formset(self):
        return forms.StrengthsFormset(
            self.request.POST if self.request.POST else None,
            instance=self.card,
        )

    def post(self, request, card_id):
        recommendations_formset = self.get_recommendations_formset()
        strengths_formset = self.get_strengths_formset()
        
        if recommendations_formset.is_valid():
            recommendations_formset.save()
        
        if strengths_formset.is_valid():
            strengths_formset.save()
            
        return redirect(reverse_lazy(
            "personal_cards:card", kwargs={"card_id": card_id}
        ))
