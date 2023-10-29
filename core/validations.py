from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

UserModel = get_user_model()

def custom_validation(data):
    email = data['email'].strip()
    rut = data['rut'].strip()
    password = data['password'].strip()

    if not email or UserModel.objects.filter(email=email).exists():
        raise ValidationError('choose another email')

    if not password or len(password) < 8:
        raise ValidationError('choose another password, min 8 characters')

    if not rut or UserModel.objects.filter(rut=rut).exists():  # Corregido el filtro por rut
        raise ValidationError('choose another rut')

    return data


def validate_email(data):
    email = data['email'].strip()
    if not email:
        raise ValidationError('an email is needed')
    return True

def validate_rut(data):
    rut = data['rut'].strip()
    if not rut:
        raise ValidationError('choose another rut')
    return True

def validate_password(data):
    password = data['password'].strip()
    if not password:
        raise ValidationError('a password is needed')
    return True