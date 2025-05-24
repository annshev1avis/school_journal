from django import forms

import apps.personal_cards.models as models


RecommendationsFormset = forms.inlineformset_factory(
    parent_model=models.PersonalMonthCard,
    model=models.PersonalRecommendations,
    fields=["text"],
    extra=0,
)


StrengthsFormset = forms.inlineformset_factory(
    parent_model=models.PersonalMonthCard,
    model=models.PersonalStrength,
    fields=["text"],
    extra=0,
)
