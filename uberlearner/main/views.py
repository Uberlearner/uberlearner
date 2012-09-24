from django.views.generic.simple import direct_to_template

def under_construction(request):
    return direct_to_template(
        request,
        'under-construction.html',
        extra_context={'main_js_module': '../../uberlearner/js/main/under-costruction'}
    )
