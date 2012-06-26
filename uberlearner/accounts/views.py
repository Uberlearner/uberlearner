from django.http import HttpResponse, HttpResponseRedirect
import allauth.account
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User

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

def user_profile_with_username(request, username=''):
    user = get_object_or_404(User, username=username)
    return render_to_response('allauth/account/profile.html',
                              {'profile_owner': user},
                              context_instance=RequestContext(request))

@login_required
def user_profile(request):
    user = request.user
    return render_to_response('allauth/account/profile.html',
                              {'profile_owner': user},
                              context_instance=RequestContext(request))
