import os
import sys

path = '/home/ubuntu/projects/uberlearner/uberlearner'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'uberlearner.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
