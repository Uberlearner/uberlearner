from django.conf import settings
from django.conf.urls.defaults import *

from accounts.forms import CaptchaSignupForm

from allauth.account import views as allauth_views
from accounts import views as accounts_views
from django.core.urlresolvers import reverse

urlpatterns = patterns("",
    url(r"^email/$", allauth_views.email, name="account_email"),
    url(r"^signup/$", allauth_views.signup, {
        'template_name': 'allauth/account/signup.html',
        'verification_sent_template': 'allauth/account/verification_sent.html',
        'form_class': CaptchaSignupForm,
    }, name="account_signup"),
    url(r"^login/$", accounts_views.login, {
        'template_name': 'allauth/account/login.html',
        'verification_sent_template': 'allauth/account/verification_sent.html',        
    }, name="account_login"),
    url(r"^password/change/$", allauth_views.password_change, name="account_change_password"),
    url(r"^password/set/$", allauth_views.password_set, name="account_set_password"),
    url(r"^logout/$", allauth_views.logout, {
        'next_page': '/'
    }, name="account_logout"),
    
    url(r"^confirm_email/(\w+)/$", "emailconfirmation.views.confirm_email", name="account_confirm_email"),
    
    # password reset
    url(r"^password/reset/$", allauth_views.password_reset, name="account_reset_password"),
    url(r"^password/reset/done/$", allauth_views.password_reset_done, name="account_reset_password_done"),
    url(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", allauth_views.password_reset_from_key, name="account_reset_password_from_key"),
    
    # user profile
    url(r"^profile/$", accounts_views.user_profile, name="account_user_profile"),
)