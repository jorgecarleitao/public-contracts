def set_up_django_environment(settings):
    import os
    import sys
    import django

    # Adds the previous path to the working path so we have access to 'contracts'

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    if path not in sys.path:
        sys.path.insert(1, path)
    del path

    # Sets Django settings to be the settings in this directory
    os.environ['DJANGO_SETTINGS_MODULE'] = settings

    django.setup()
