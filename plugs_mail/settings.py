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

# Default Settings
PROJECT_SETTINGS['OVERRIDE_TEMPLATE_DIR'] = PROJECT_SETTINGS.get('OVERRIDE_TEMPLATE_DIR', None)

app_settings = PROJECT_SETTINGS
