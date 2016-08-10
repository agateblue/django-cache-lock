from django.conf import settings

SETTINGS_ATTR = 'CACHE_LOCK'
USER_SETTINGS = None



DEFAULTS = {
    'CACHE_ALIAS': 'default',
    'CACHE_KEY_PREFIX': 'cache_lock',
    'DEFAULT_LOCK_TIMEOUT': 60,
    'ENABLED': True,
}


class Settings(object):
    """
    Borrowed from rest_framework
    A settings object, that allows API settings to be accessed as properties.
    For example:

        from rest_framework.settings import api_settings
        print(api_settings.DEFAULT_RENDERER_CLASSES)

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """
    def __init__(self, defaults=None):
        self.defaults = defaults or DEFAULTS

    @property
    def user_settings(self):
        return getattr(settings, SETTINGS_ATTR, {})

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid preference setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Cache the result
        # We sometimes need to bypass that, like in tests
        if getattr(settings, 'CACHE_DYNAMIC_PREFERENCES_SETTINGS', True):
            setattr(self, attr, val)
        return val


app_settings = Settings(DEFAULTS)
