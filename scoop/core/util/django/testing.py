# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.test.runner import DiscoverRunner


class CeleryTestSuiteRunner(DiscoverRunner):
    """ Test runner configuré pour exécuter les tâches Celery immédiatement """

    def setup_test_environment(self, **kwargs):
        super(CeleryTestSuiteRunner, self).setup_test_environment(**kwargs)
        # Désactiver la communication avec celery, exécuter directement les tâches
        settings.CELERY_ALWAYS_EAGER = True
