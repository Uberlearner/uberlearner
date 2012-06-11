from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def navactive (request, urls, css_active_class="active", css_inactive_class=""):
    """
    This is a simple template tag that is placed as a part of the class
    attribute of the links in the navigation bar. It requires the request
    object as its first parameter, a space separated list of paths for which
    the navigation link is to be marked active as the second argument and the 
    strings to be returned in the events that the navigation link is to be 
    active/inactive.
    """
    if request.path in (reverse(url) for url in urls.split()):
        return css_active_class
    return css_inactive_class