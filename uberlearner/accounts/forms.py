from allauth.account.forms import SignupForm
from captcha.fields import ReCaptchaField
from django import forms
from main.widgets import DateWidget
from avatar.settings import AVATAR_DEFAULT_SIZE
from avatar.forms import avatar_img, UploadAvatarForm
from django.forms import widgets
from accounts.widgets import ImageRadioSelectRenderer

class CaptchaSignupForm(SignupForm):
    captcha = ReCaptchaField(attrs={'theme': 'clean'})
    
class UserProfileForm(UploadAvatarForm):
    first_name = forms.CharField(label='First name', required=False)
    last_name = forms.CharField(label='Last name', required=False)
    summary = forms.CharField(label='Summary', widget=forms.Textarea, required=False)

    def wrap_clean_avatar(self, clean_avatar):
        def wrapped_clean_avatar():
            if not self.cleaned_data['avatar']:
                return
            return clean_avatar()
        return wrapped_clean_avatar
    
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['avatar'].required = False
        self.clean_avatar = self.wrap_clean_avatar(self.clean_avatar)
        
class ReplacementPrimaryAvatarForm(forms.Form):    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        size = kwargs.pop('size', AVATAR_DEFAULT_SIZE)
        avatars = kwargs.pop('avatars')
        super(ReplacementPrimaryAvatarForm, self).__init__(*args, **kwargs)
        self.fields['choice'] = forms.ChoiceField(
            choices=[(c.id, avatar_img(c, size)) for c in avatars],
            widget=widgets.RadioSelect(renderer=ImageRadioSelectRenderer))
