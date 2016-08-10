# -*- coding: utf-8 -*-
import time
from django.db import models
from django.utils.functional import cached_property

from . import exceptions
from . import lock


class LockMixin(models.Model):

    lock_required = False  # whether a lock is required to call .save() on this model

    class Meta:
        abstract = True

    @cached_property
    def locker(self):
        return lock.Locker()

    @property
    def _lock_key(self):
        if not self.pk:
            raise exceptions.InvalidLock('Cannot get lock key for unsaved model')
        model_name = self._meta.app_label
        parts = [
            'models',
            self._meta.label,
            str(self.pk),
        ]
        return ':'.join(parts)

    @property
    def current_lock(self):
        return self.locker.get(self._lock_key)

    def lock(self):
        return lock.LockContextManager(
            key=self._lock_key)

    def acquire_lock(self):
        return self.locker.acquire(self._lock_key)

    def release_lock(self):
        self.locker.release(self._lock_key)

    def save(self, *args, **kwargs):
        if self.pk:
            self.check_lock()
        super(LockMixin, self).save(*args, **kwargs)

    def check_lock(self):
        if not self.lock_required:
            return
        current_lock = self.current_lock
        if not current_lock:
            raise exceptions.WriteWithoutLock('Tried to save a lock-required model row without locking it first')
