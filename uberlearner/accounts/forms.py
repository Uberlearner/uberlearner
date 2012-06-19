from allauth.account.forms import SignupForm
from captcha.fields import ReCaptchaField

class CaptchaSignupForm(SignupForm):
    captcha = ReCaptchaField(attrs={'theme': 'clean'})