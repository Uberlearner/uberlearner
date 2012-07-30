from django.forms.widgets import RadioFieldRenderer
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode

class ImageRadioSelectRenderer(RadioFieldRenderer):
    def render(self):
        return mark_safe(u'<ul class="thumbnails">\n%s\n</ul>' % u'\n'.join([u'<li class="thumbnail">%s</li>'
                % force_unicode(w) for w in self]))