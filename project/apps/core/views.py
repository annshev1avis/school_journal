from django import forms
from django.db import models


class FiltersForm(forms.Form):
    def make_fields_unrequired(self):
        for field_name in self.fields:
            self.fields[field_name].required = False


class ListFiltersMixin:
    """
    Миксин добавляет форму фильтрации в верхнюю часть страницы.
    Поля формы основаны на filter_fields, все поля получают blank=True.
    
    filter_fields - поля self.model, по которым будет производится 
    фильтрация. Записывается в виде списка строк
    """
    filter_fields = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_filters_form(self):
        form = FiltersForm(data=self.request.GET)
        
        for model_field_name in self.filter_fields:
            model_field = getattr(self.model, model_field_name)
            form.fields[model_field_name] = model_field.field.formfield()
        
        form.make_fields_unrequired()
        return form
    
    def dispatch(self, request, *args, **kwargs):
        self.filters_form = self.get_filters_form()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        
        if not self.filters_form.is_bound:
            return queryset
        
        if not self.filters_form.is_valid():
            return queryset
        
        filters = {
            key: value for key, value 
            in self.filters_form.cleaned_data.items()
            if value
        }
        
        return queryset.filter(**filters)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filters_form"] = self.filters_form
        return context
