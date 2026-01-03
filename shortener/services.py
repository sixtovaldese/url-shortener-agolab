from datetime import timedelta
from django.utils import timezone
from django.conf import settings
import secrets
import string


def calculate_expiry(user=None):
    expiry_days = settings.AUTH_EXPIRY_DAYS if user else settings.ANON_EXPIRY_DAYS
    return timezone.now() + timedelta(days=expiry_days)


def generate_random_code(length=6):
    charset = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(charset) for _ in range(length))


def validate_custom_alias(alias):
    min_length = settings.MIN_ALIAS_LENGTH
    
    if len(alias) < min_length:
        return False, f"El alias debe tener al menos {min_length} caracteres"
    
    if not alias.isalnum():
        return False, "El alias solo puede contener letras y números"
    
    return True, ""