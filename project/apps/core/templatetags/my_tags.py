from django import template

register = template.Library()

@register.simple_tag
def link_is_active(url_beginning, request):
    if request.path[:len(url_beginning)] == url_beginning:
        return "active"
    return ""