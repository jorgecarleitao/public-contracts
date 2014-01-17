import os
import sys

#path to directory of the .wgsi file ('[directory]/')
wsgi_dir = os.path.abspath(os.path.dirname(__file__))

# path to project root directory (osqa '/')
project_dir = os.path.dirname(wsgi_dir)

# add project  directory to system's Path
sys.path.append(project_dir)
sys.path.append('/home/littlepig/webapps/public_contracts/public-contracts/main')

os.environ['DJANGO_SETTINGS_MODULE'] = 'main.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
