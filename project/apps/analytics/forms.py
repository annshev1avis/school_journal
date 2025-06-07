from django import forms

from apps.core.constants import STUDING_MONTHES_DICT


class PeriodForm(forms.Form):
    start_month = forms.ChoiceField(
        choices=list(STUDING_MONTHES_DICT.items()),
        initial=1,
        label="Начало периода",
        required=False,
    )
    end_month = forms.ChoiceField(
        choices=list(STUDING_MONTHES_DICT.items()),
        initial=10,
        label="Конец периода",
        required=False,
    )
        
    def clean(self):
        cleaned_data = super().clean()
        
        if cleaned_data.get("start_month") and cleaned_data.get("end_month"):
            if not (int(cleaned_data["start_month"]) <= int(cleaned_data["end_month"])):
                raise forms.ValidationError("Конец периода должен быть позже начала")
            
        return cleaned_data
