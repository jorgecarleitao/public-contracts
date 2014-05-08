from django.core.urlresolvers import resolve
from main.domain import SITE_NAME, SITE_DOMAIN


def site(request):
    """
    Returns context variables of the website
    """
    try:
        tab = resolve(request.path).app_name
    except:
        tab = 'main'

    return {'SITE_NAME': SITE_NAME,
            'SITE_DOMAIN': SITE_DOMAIN,
            'main_navigation_tab': tab}
