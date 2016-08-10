from django.db import models

from cache_lock.models import LockMixin


class TestModel(LockMixin):
    lock_required = True
    title = models.CharField(max_length=100)
