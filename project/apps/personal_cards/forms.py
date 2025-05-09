from django import forms

from apps.core.models import Campus, Group


class FiltersForm(forms.Form):
    group = forms.ChoiceField(
        label="Класс",
        choices=[
            (group.id, str(group)) 
            for group in Group.objects.all()
        ]
    )
