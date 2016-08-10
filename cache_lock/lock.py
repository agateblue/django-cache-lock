try:
    from collections import ChainMap
except ImportError:
    from chainmap import ChainMap

from django.core.cache import caches
from .settings import app_settings
from . import exceptions


class ConfigContextManager(object):
    def __init__(self, obj, new_config):
        self.obj = obj
        self.new_config = new_config

    def __enter__(self):
        self.old_config = self.obj.config
        self.obj.config = self.new_config

    def __exit__(self, type, value, traceback):
        self.obj.config = self.old_config


    def __init__(self, **kwargs):
        self._config = {}
        self._config['timeout'] = kwargs.get('timeout', app_settings.DEFAULT_LOCK_TIMEOUT)
        self._config['enabled'] = kwargs.get('enabled', app_settings.ENABLED)

        self.config = self._config

    def
    def build_key(self, key):
        return ':'.join([app_settings.CACHE_KEY_PREFIX, key])

    @property
    def cache(self):
        return caches[app_settings.CACHE_ALIAS]

    def acquire(self, key, wait=False):
        current = self.get(key)
        if not current:
            # great, we can acquire the lock
            return self.set(key)
        raise exceptions.AlreadyLocked('Tried to lock an already-locked key')

    def get(self, key):
        final_key = self.build_key(key)
        return self.cache.get(final_key, 0)

    def set(self, key):
        final_key = self.build_key(key)
        return self.cache.set(final_key, 1, self.config['timeout'])

    def release(self, key):
        final_key = self.build_key(key)
        return self.cache.delete(final_key)


class LockContextManager(object):
    def __init__(self, key):
        self.key = key
        self.locker = Locker()

    def __enter__(self):
        self.locker.acquire(self.key)

    def __exit__(self, type, value, traceback):
        self.locker.release(self.key)

lock = LockContextManager
