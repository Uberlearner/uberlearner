from django.conf.urls import patterns, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    url(r'^terms/$', direct_to_template, {
        'template': 'flatpages/terms.html',
        'extra_context': {
            'main_js_module': 'uberlearner/js/flatpages/base'
        }
    }, name='flatpages.terms'),
    url(r'^about/$', direct_to_template, {
        'template': 'flatpages/about.html',
        'extra_context': {
            'main_js_module': 'uberlearner/js/flatpages/base'
        }
    }, name='flatpages.about'),
    url(r'^privacy/$', direct_to_template, {
        'template': 'flatpages/privacy.html',
        'extra_context': {
            'main_js_module': 'uberlearner/js/flatpages/base'
        }
    }, name='flatpages.privacy'),
    url(r'^contact-us/$', direct_to_template, {
        'template': 'flatpages/contact-us.html',
        'extra_context': {
            'main_js_module': 'uberlearner/js/flatpages/base'
        }
    }, name='flatpages.contact'),
)