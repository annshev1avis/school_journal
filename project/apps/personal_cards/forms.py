from django import forms

import apps.personal_cards.models as models


RecommendationsFormset = forms.inlineformset_factory(
    parent_model=models.PersonalMonthCard,
    model=models.PersonalRecommendations,
    fields=["text"],
    widgets={"text": forms.Textarea(attrs={"rows": None})},
    extra=0,
)


StrengthsFormset = forms.inlineformset_factory(
    parent_model=models.PersonalMonthCard,
    model=models.PersonalStrength,
    fields=["text"],
    widgets={"text": forms.Textarea(attrs={"rows": None})},
    extra=0,
)
