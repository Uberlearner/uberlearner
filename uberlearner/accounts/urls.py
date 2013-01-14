from django.conf import settings
from django.conf.urls.defaults import *
from accounts.forms import CaptchaSignupForm, ReplacementPrimaryAvatarForm
from allauth.account import views as allauth_views
from accounts import views as accounts_views
from django.core.urlresolvers import reverse_lazy
from courses.views import CourseList

urlpatterns = patterns("",
    url(r"^signup/$", accounts_views.signup, {
        'template_name': 'accounts/signup/index.html',
        'verification_sent_template': 'allauth/account/verification_sent.html',
        'form_class': CaptchaSignupForm,
    }, name="account_signup"),
    url(r"^login/$", accounts_views.login, {
        'template_name': 'accounts/login/index.html',
        'verification_sent_template': 'allauth/account/verification_sent.html',
        'extra_context': {
            'main_js_module': 'uberlearner/js/main/base.js'
        },
        'logged_in_view': CourseList.as_view()
    }, name="account_login"),
    url(r"^password/change/$", allauth_views.password_change, name="account_change_password"),
    url(r"^password/set/$", allauth_views.password_set, name="account_set_password"),
    url(r"^logout/$", allauth_views.logout, {
        'next_page': '/'
    }, name="account_logout"),
    
    url(r"^confirm_email/(?P<key>\w+)/$", accounts_views.ConfirmEmailView.as_view(
        email_confirm_template='accounts/email/confirmation/email_confirm.html',
        email_confirmed_template='accounts/email/confirmation/email_confirmed.html',
    ), name="account_confirm_email"),
    
    # password reset
    url(r"^password/reset/$", allauth_views.password_reset, {
        'template_name': 'accounts/email/password_reset/password_reset.html'
    }, name="account_reset_password"),
    url(r"^password/reset/done/$", allauth_views.password_reset_done, {
        'template_name': 'accounts/email/password_reset/password_reset_done.html'
    }, name="account_reset_password_done"),
    url(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", accounts_views.password_reset_from_key, {
        'template_name': 'accounts/email/password_reset/password_reset_from_key.html'
    }, name="account_reset_password_from_key"),
    
    # user profile
    url(r"^profile/$", accounts_views.user_profile, name="account_user_profile"),
#    url(r'^profile/avatar/add/$', 'avatar.views.add', name='avatar_add'),
#    url(r'^profile/avatar/change/$', 'avatar.views.change', {
#            'next_override': reverse_lazy('account_edit_user_profile'),
#            'primary_form': ReplacementPrimaryAvatarForm, 
#        }, name='avatar_change'),
#    url(r'^profile/avatar/delete/$', 'avatar.views.delete', name='avatar_delete'),
#    url(r'^profile/avatar/render_primary/(?P<user>[\+\w]+)/(?P<size>[\d]+)/$', 'avatar.views.render_primary', name='avatar_render_primary'),   
    url(r"^profile/(?P<username>[0-9a-zA-Z@.+-_]+)/edit/$", accounts_views.edit_user_profile_with_username, name="account_edit_user_profile_with_username"),
    url(r"^profile/edit/$", accounts_views.edit_user_profile, name="account_edit_user_profile"),
    url(r"^profile/(?P<username>[0-9a-zA-Z@.+-_]+)/$", accounts_views.user_profile_with_username, name="account_user_profile_with_username"),
)
