"""
Plugs Mail Utils
"""

def to_email(email_class, email, **data):
    """
    Send email to specified email address
    """
    email_class().send([email], **data)

def to_user(email_class, user, **data):
    """
    Email user
    """
    email_class().send([user.email], **data)

def to_staff(email_class, **data):
    """
    Email staff users
    """
    for user in get_user_model().objects.filter(is_staff=True):
        email_class().send([user.email], **data)

def to_superuser(email_class, **data):
    """
    Email superusers
    """
    for user in get_user_model().objects.filter(is_superuser=True):
        email_class().send([user.email], **data)
