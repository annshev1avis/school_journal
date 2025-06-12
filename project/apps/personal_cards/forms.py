from django import forms
from django.core.exceptions import ValidationError

import apps.personal_cards.models as models


class CreateCardsForm(forms.Form):
    start_date = forms.DateField(
        label="Начало периода", widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        label="Конец периода", widget=forms.DateInput(attrs={'type': 'date'})
    )
    add_softskills = forms.BooleanField(
        label="Добавить поля для оценивания межпредметных навыков",
        initial=False,
        required=False,
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        start_date = cleaned_data["start_date"]
        end_date = cleaned_data["end_date"]
        
        if not start_date <= end_date:
            raise ValidationError("Начало периода должно быть раньше конца")


RecommendationsFormset = forms.inlineformset_factory(
    parent_model=models.PersonalCard,
    model=models.PersonalRecommendations,
    fields=["text"],
    widgets={"text": forms.Textarea(attrs={"rows": None})},
    extra=0,
)


StrengthsFormset = forms.inlineformset_factory(
    parent_model=models.PersonalCard,
    model=models.PersonalStrength,
    fields=["text"],
    widgets={"text": forms.Textarea(attrs={"rows": None})},
    extra=0,
)
