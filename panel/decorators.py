from functools import wraps
from panel.utils import get_client_ip
from django.conf import settings
from django.core.exceptions import PermissionDenied


def vpn_decorator(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        client_ip = get_client_ip(args[0])
        if client_ip != settings.ALLOWED_VPN_IP:
            print(f"[Permission Denied] Invalid IP {client_ip}")
            raise PermissionDenied
        return function(*args, **kwargs)

    return decorator

