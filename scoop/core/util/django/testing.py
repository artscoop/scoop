# coding: utf-8
from django.conf import settings
from django.test.runner import DiscoverRunner
from scoop.core.util.stream.directory import Paths


class CeleryTestSuiteRunner(DiscoverRunner):
    """ Test runner configuré pour exécuter les tâches Celery immédiatement """

    def setup_test_environment(self, **kwargs):
        super(CeleryTestSuiteRunner, self).setup_test_environment(**kwargs)
        # Désactiver la communication avec celery, exécuter directement les tâches
        settings.CELERY_ALWAYS_EAGER = False


# Configuration settings pour les tests
TEST_CONFIGURATION = {
    'EMAIL_BACKEND': 'django.core.mail.backends.filebased.EmailBackend',
    'EMAIL_FILE_PATH': Paths.get_root_dir('files', 'tests', 'mail'),
    'DEFAULT_FROM_EMAIL': 'admin@test.com',
    'MESSAGING_DEFAULT_THREAD_QUOTA': 32
}
