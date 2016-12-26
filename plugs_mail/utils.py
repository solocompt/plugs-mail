"""
Plugs Mail Utils
"""

from django.contrib.auth import get_user_model

def to_email(email_class, email, language=None, **data):
    """
    Send email to specified email address
    """
    email_class().send([email], language=language, **data)

def to_user(email_class, user, language=None, **data):
    """
    Email user
    """
    email_class().send([user.email], language=language, **data)

def to_staff(email_class, language=None, **data):
    """
    Email staff users
    """
    for user in get_user_model().objects.filter(is_staff=True):
        email_class().send([user.email], language=language, **data)

def to_superuser(email_class, language=None, **data):
    """
    Email superusers
    """
    for user in get_user_model().objects.filter(is_superuser=True):
        email_class().send([user.email], language=language, **data)
