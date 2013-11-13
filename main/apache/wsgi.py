import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
packages = os.path.join(root, '/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')

sys.path.insert(0, packages)
sys.path.insert(0, root)

os.environ['DJANGO_SETTINGS_MODULE'] = 'main.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
