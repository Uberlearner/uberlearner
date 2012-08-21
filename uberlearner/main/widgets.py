from django import forms

class DateWidget(forms.DateInput):
    """
    A jquery-ui based widget. Assumes that jquery and jquery-ui are available.
    These files will be served through the google cdn and will not be served from
    this site.
    """
    class Media:
        js = ('uberlearner/js/accounts/edit_profile.js', )
    
    def __init__(self, attrs=None, format=None):
        compiled_attrs = {'class': 'date-widget'}
        if attrs is not None:
            compiled_attrs.update(attrs)
        super(DateWidget, self).__init__(attrs=compiled_attrs, format=format)