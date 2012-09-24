from django.http import HttpResponse, HttpResponseRedirect
import allauth.account
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, render
from django.template import RequestContext
from django.contrib.auth.models import User
from accounts.forms import UserProfileForm
from avatar.views import _get_avatars
from avatar.models import Avatar
from avatar.signals import avatar_updated

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

def user_profile_with_username(request, username='', user=None):
    if not user:
        user = get_object_or_404(User, username=username)
    return render_to_response('allauth/account/view_profile.html',
                              {'profile_owner': user, 'main_js_module': 'uberlearner/js/accounts/profile-view'},
                              context_instance=RequestContext(request))

@login_required
def user_profile(request):
    return HttpResponseRedirect(reverse('account_user_profile_with_username', 
                                kwargs={'username': request.user.username}))

@login_required
def edit_user_profile_with_username(request, username=''):
    if request.user and request.user.username != username:
        raise PermissionDenied("You can't edit another user's profile")
    user = get_object_or_404(User, username=username)
    avatar, avatars = _get_avatars(request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            if 'avatar' in request.FILES:
                avatar = Avatar(user=user, primary=True)
                image_file = request.FILES['avatar']
                avatar.avatar.save(image_file.name, image_file)
                avatar.save()
                avatar_updated.send(sender=Avatar, user=user, avatar=avatar)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.profile.dob = form.cleaned_data['dob']
            user.profile.summary = form.cleaned_data['summary']
            user.profile.save()
            user.save()
            return user_profile_with_username(request, '', user)
    else:
        form = UserProfileForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'dob': user.profile.dob,
            'summary': user.profile.summary,
            'avatar': avatar
        }, user=user)

    return render(request, 'allauth/account/edit_profile.html', {
        'form': form,
        'main_js_module': 'uberlearner/js/accounts/profile-edit'
    }) 

def edit_user_profile(request):
    return HttpResponseRedirect(
        reverse('account_edit_user_profile_with_username',
            kwargs={'username': request.user.username})
    )



