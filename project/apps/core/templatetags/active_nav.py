from django import template
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

register = template.Library()

@register.simple_tag
def link_is_active(view_name, request):
    try:
        url_beginning  = reverse(view_name)
    except NoReverseMatch:
        return ""
    
    print(len(url_beginning), request.path, request.path[:len(url_beginning)], url_beginning)
    if request.path[:len(url_beginning)] == url_beginning:
        return "active"
    return ""