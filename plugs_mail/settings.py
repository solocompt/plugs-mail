"""
Plugs Mail Settings
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


MANDATORY_SETTINGS = ['SEND_EMAILS']
PROJECT_SETTINGS = getattr(settings, 'PLUGS_MAIL', {})


for setting in MANDATORY_SETTINGS:
    try:
        PROJECT_SETTINGS[setting]
    except KeyError:
        raise ImproperlyConfigured('Missing setting: PLUGS_MAIL[\'{0}\']'.format(setting))


app_settings = PROJECT_SETTINGS
