from allauth.account import signals
from allauth.account.forms import ResetPasswordKeyForm, ChangePasswordForm
from avatar.forms import UploadAvatarForm
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseNotAllowed
import allauth.account
import allauth.account.views
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.utils.http import base36_to_int
from django.utils.translation import ugettext
from django.views.decorators.http import require_POST, require_GET
from django.views.generic import TemplateView
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.template import RequestContext
from django.contrib.auth.models import User
from accounts.forms import UserProfileForm
from avatar.views import _get_avatars
from avatar.models import Avatar
from avatar.signals import avatar_updated
from courses.models import Course

def login(request, **kwargs):
    """
    This view is an envelope for the default login view of allauth.account.
    In case the user is already authenticated, this view redirects the user
    to the user-profile page. If not, the regular actions are taken to log
    the user into the system.
    """
    if request.user.is_authenticated():
        return kwargs.get('logged_in_view')(request, **kwargs)
    else:
        return allauth.account.views.login(request, **kwargs)

def signup(request, **kwargs):
    """
    This view is an envelope for the default signup view of the allauth.account.
    In case the user is already authenticated, this view redirects the user
    to the user-profile page. If not, the regular actions are taken to log
    the user into the system.
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account_user_profile'))
    else:
        return allauth.account.views.signup(request, **kwargs)

class UserProfileWithUsername(TemplateView):
    template_name = 'allauth/account/view_profile/index.html'

    def are_enrollments_visible(self, profile_owner):
        """
        Returns true if the user is enrolled in any course.
        """
        return profile_owner.enrollments.all().exists()

    def are_instructor_courses_visible(self, profile_owner):
        """
        Returns true if the instructor's profile should contain courses taught
        """
        #if instructor is the viewer and there are courses (public or private) then return true
        if self.request.user.username == profile_owner.username:
            return Course.all_objects.filter(instructor=profile_owner).exists()
        #if viewer is not the instructor, then return true if there are publicly viewable courses
        else:
            return Course.objects.filter(instructor=profile_owner).exists()

    def get_context_data(self, **kwargs):
        context_data = super(UserProfileWithUsername, self).get_context_data(**kwargs)
        context_data['profile_owner'] = get_object_or_404(User, username=kwargs['username'])
        context_data['main_js_module'] = 'uberlearner/js/accounts/profile-view.js'
        context_data['are_enrollments_visible'] = self.are_enrollments_visible(context_data['profile_owner'])
        context_data['are_instructor_courses_visible'] = self.are_instructor_courses_visible(context_data['profile_owner'])
        return context_data

@login_required
def user_profile(request):
    return HttpResponseRedirect(reverse('account_user_profile_with_username', 
                                kwargs={'username': request.user.username}))

@login_required
@require_GET
def edit_user_profile_with_username(request, username):
    if request.user and request.user.username != username:
        raise PermissionDenied("You can't edit another user's profile")
    user = request.user
    avatar, avatars = _get_avatars(user)
    if 'basic_info_form' in request.session:
        basic_info_form = request.session.pop('basic_info_form')
    else:
        basic_info_form = UserProfileForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'summary': user.profile.summary,
            'avatar': avatar
        }, user=user)
    if 'change_password_form' in request.session:
        change_password_form = request.session.pop('change_password_form')
    else:
        change_password_form = ChangePasswordForm(user=user)

    return render(request, 'allauth/account/edit_profile/index.html', {
        'basic_info_form': basic_info_form,
        'change_password_form': change_password_form,
        'main_js_module': 'uberlearner/js/accounts/profile-edit'
    })

@login_required
@require_POST
def edit_user_profile_basic_info(request, username):
    if request.user and request.user.username != username:
        raise PermissionDenied("You can't edit another user's profile")
    user = request.user
    avatar, avatars = _get_avatars(request.user)
    form = UserProfileForm(request.POST, request.FILES, user=user)
    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, "Your profile has been successfully updated")
        return redirect('account_user_profile_with_username', username=user.username)
    else:
        messages.add_message(request, messages.ERROR, "Your profile could not be updated")
        request.session['basic_info_form'] = form
        return redirect(reverse('account_edit_user_profile_with_username', kwargs={
            'username':user.username
        }) + '#!/basic-info-tab')

@login_required
@require_POST
def edit_user_profile_change_password(request, username, **kwargs):
    if request.user and request.user.username != username:
        raise PermissionDenied("You can't edit another user's profile")
    user = request.user

    form = ChangePasswordForm(user, request.POST)
    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, "Password successfully updated")
        return redirect('account_user_profile_with_username', username=user.username)
    else:
        messages.add_message(request, messages.ERROR, "Could not update password")
        request.session['change_password_form'] = form
        return redirect(reverse('account_edit_user_profile_with_username', kwargs={
            'username':user.username
        }) + "#!/accounts-tab")

def edit_user_profile(request):
    return HttpResponseRedirect(
        reverse('account_edit_user_profile_with_username',
            kwargs={'username': request.user.username})
    )

class ConfirmEmailView(allauth.account.views.ConfirmEmailView):
    """
    This view class over-rides the one provided by django-allauth. The reason for the over-ride is to be
    able to use a different template file name than the one that is hard-coded into django-allauth.
    """
    email_confirm_template = None
    email_confirmed_template = None

    def __init__(self, email_confirm_template='account/email_confirm.html',
                 email_confirmed_template='account/email_confirmed.html', **kwargs):
        self.email_confirm_template = email_confirm_template
        self.email_confirmed_template = email_confirmed_template
        super(ConfirmEmailView, self).__init__(**kwargs)

    def get_template_names(self):
        if self.request.method == "GET":
            return [self.email_confirm_template]
        elif self.request.method == "POST":
            return [self.email_confirmed_template]

def password_reset_from_key(request, uidb36, key, **kwargs):
    """
    This view replaces the view provided by allauth for the actual password reset. Since this view was
    not a class, it could not be extended.
    TODO: convert this view to a class-based view and send the changes upstream.
    """
    form_class = kwargs.get("form_class", ResetPasswordKeyForm)
    template_name = kwargs.get("template_name", "account/password_reset_from_key.html")
    token_generator = kwargs.get("token_generator", default_token_generator)

    # pull out user
    try:
        uid_int = base36_to_int(uidb36)
    except ValueError:
        raise Http404

    user = get_object_or_404(User, id=uid_int)

    if token_generator.check_token(user, key):
        if request.method == "POST":
            password_reset_key_form = form_class(request.POST, user=user, temp_key=key)
            if password_reset_key_form.is_valid():
                password_reset_key_form.save()
                messages.add_message(request, messages.SUCCESS,
                    ugettext(u"Password successfully changed.")
                )
                signals.password_reset.send(sender=request.user.__class__,
                    request=request, user=request.user)
                password_reset_key_form = None
                return redirect('account_login')
        else:
            password_reset_key_form = form_class()
        ctx = { "form": password_reset_key_form, }
    else:
        ctx = { "token_fail": True, }

    return render_to_response(template_name, RequestContext(request, ctx))