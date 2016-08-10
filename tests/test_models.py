#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-cache-lock
------------

Tests for `django-cache-lock` models module.
"""
import time

from django.test import TestCase

from cache_lock import lock, exceptions
from .test_app import models
from .utils import test_concurrently

class TestCache_lock(TestCase):

    def setUp(self):
        self.locker = lock.Locker()

    def test_cannot_lock_unsaved_model(self):
        m = models.TestModel()
        with self.assertRaises(exceptions.InvalidLock):
            m.acquire_lock()

    def test_can_acquire_lock_on_model(self):
        m = models.TestModel.objects.create(title="test")

        m = models.TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.current_lock, 0)
        m.acquire_lock()
        self.assertEqual(m.current_lock, 1)
        try:
            m.save()
        finally:
            m.release_lock()

        self.assertEqual(m.current_lock, 0)

    def test_lock_context_manager(self):
        m = models.TestModel.objects.create(title="test")

        self.assertEqual(m.current_lock, 0)

        with m.lock():
            self.assertEqual(m.current_lock, 1)

        self.assertEqual(m.current_lock, 0)

    def test_can_lock_arbitrary_block(self):

        self.assertEqual(self.locker.get('test'), 0)

        with lock.lock('test'):
            self.assertEqual(self.locker.get('test'), 1)

        self.assertEqual(self.locker.get('test'), 0)

    def test_concurrent_locking(self):
        results = []
        concurrency = 10
        @test_concurrently(concurrency)
        def concurrent():
            try:
                with lock.lock('test'):
                    results.append(True)
                    time.sleep(0.1)
            except exceptions.AlreadyLocked:
                results.append(False)

        concurrent()

        # Only the thread should have acquire the lock
        self.assertTrue(results[0])
        for i in range(1, concurrency):
            self.assertFalse(results[i])

    def test_can_override_locker_config(self):
        locker = lock.Locker()

        self.assertTrue(locker.config['enabled'])
        self.assertEqual(locker.config['timeout'], 60)

        with locker.configure(enabled=False):
            self.assertFalse(locker.config['enabled'])

        self.assertTrue(locker.config['enabled'])
        self.assertEqual(locker.config['timeout'], 60)

    def tearDown(self):
        self.locker.cache.clear()
