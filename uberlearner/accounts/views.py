from django.http import HttpResponse, HttpResponseRedirect
import allauth.account
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template

def login(request, **kwargs):
    """
    This view is an envelope for the default login view of allauth.account.
    In case the user is already authenticated, this view redirects the user
    to the user-profile page. If not, the regular actions are taken to log
    the user into the system.
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account_user_profile'))
    else:
        return allauth.account.views.login(request, **kwargs)

def user_profile(request):
    return direct_to_template(request, 'allauth/account/profile.html')