from main.domain import SITE_NAME, SITE_DOMAIN


def site(request):
    """
    Returns context variables of the website
    """
    return {'SITE_NAME': SITE_NAME, 'SITE_DOMAIN': SITE_DOMAIN}
