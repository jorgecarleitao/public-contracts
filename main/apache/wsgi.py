import os
import sys

#path to directory of the .wgsi file ('[directory]/')
wsgi_dir = os.path.abspath(os.path.dirname(__file__))

# path to project root directory (osqa '/')
project_dir = os.path.dirname(wsgi_dir)

# add project  directory to system's Path
sys.path.append(project_dir)
sys.path.append(project_dir+"/main")

os.environ['DJANGO_SETTINGS_MODULE'] = 'main.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
