"""
Plugs Mail Utils
"""

from django.utils import translation
from django.contrib.auth import get_user_model

def to_email(email_class, email, language=None, **data):
    """
    Send email to specified email address
    """
    if language:
        email_class().send([email], language=language, **data)
    else:
        email_class().send([email], translation.get_language(), **data)

def to_user(email_class, user, **data):
    """
    Email user
    """
    try:
        email_class().send([user.email], user.language, **data)
    except AttributeError:
        # this is a fallback in case the user model does not have the language field
        email_class().send([user.email], translation.get_language(), **data)

def to_staff(email_class, **data):
    """
    Email staff users
    """
    for user in get_user_model().objects.filter(is_staff=True):
        try:
            email_class().send([user.email], user.language, **data)
        except AttributeError:
            email_class().send([user.email], translation.get_language(), **data)

def to_superuser(email_class, **data):
    """
    Email superusers
    """
    for user in get_user_model().objects.filter(is_superuser=True):
        try:
            email_class().send([user.email], user.language, **data)
        except AttributeError:
            email_class().send([user.email], translation.get_language(), **data)
