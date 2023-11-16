import requests

from config.settings import Config


def send_user_registered_notify(
    email: str,
    user_id: str,
    tiny_url: str,
) -> bool:
    request = requests.post(
        f'{Config.NOTIFICATIONS_API_URL}{Config.NOTIFICATIONS_API_ENDPOINT}',
        json={'user_id': str(user_id), 'email': email, 'tiny_url': tiny_url}
    )
    status_code = getattr(request, 'status_code')
    if status_code == 200:
        return True
    else:
        return False
