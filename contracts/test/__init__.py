import requests
import requests.exceptions


def _has_remote_access():
    try:
        response = requests.get('http://www.base.gov.pt', timeout=1)
        return response.status_code == 200
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return False

HAS_REMOTE_ACCESS = _has_remote_access()
