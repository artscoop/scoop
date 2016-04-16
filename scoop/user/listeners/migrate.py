# coding: utf-8
import logging
import os
from random import shuffle

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import signals
from django.dispatch.dispatcher import receiver
from django.utils.text import slugify

from scoop.user import UserConfig


logger = logging.getLogger(__name__)


@receiver(signals.post_migrate)
def create_testuser(sender, app_config, verbosity, interactive, using, **kwargs):
    """ Traiter une migration réussie """
    if settings.USER_MIGRATION_MAKE_USERS is True and (not settings.TEST or isinstance(sender, UserConfig)):
        from scoop.user.models import Activation
        # Informations utiliasteur par défaut
        DEFAULT_ADMIN_NAME = getattr(settings, 'USER_MIGRATION_SUPERUSER_NAME', 'admin')
        DEFAULT_PASSWORD = getattr(settings, 'USER_MIGRATION_SUPERUSER_PASSWORD', 'admin')
        DEFAULT_EMAIL = getattr(settings, 'USER_MIGRATION_SUPERUSER_EMAIL', 'admin@localhost.local')
        DEFAULT_USER_COUNT = getattr(settings, 'USER_MIGRATION_DEFAULT_USER_COUNT', 0)
        current_count = get_user_model().objects.all().count()
        created_count = 0
        # Créer l'admin et le compte de test si inexistants
        try:
            get_user_model().objects.get(username=DEFAULT_ADMIN_NAME)
        except get_user_model().DoesNotExist:
            logger.info("Creating superuser with login={login} and password={password}".format(login=DEFAULT_ADMIN_NAME, password=DEFAULT_PASSWORD))
            administrator = get_user_model().objects.create_superuser(DEFAULT_ADMIN_NAME, DEFAULT_EMAIL, DEFAULT_PASSWORD)
            Activation.objects.activate(None, administrator.username)
            if not get_user_model().objects.filter(username='default').exists():
                default = get_user_model().objects.create_user('default', 'nobody@nowhere.xx', 'default')
                Activation.objects.activate(None, default.username)
        # Créer les comptes supplémentaires demandés
        with open(os.path.join(settings.STATIC_ROOT, "assets", "dictionary", "usernames.txt"), 'r') as f:
            names = [slugify(str(name.strip())).replace('-', '_') for name in f.readlines() if name.strip()]
            shuffle(names)
            DEFAULT_USER_COUNT = min(len(names), DEFAULT_USER_COUNT)
        if current_count < DEFAULT_USER_COUNT:
            for i in range(DEFAULT_USER_COUNT):
                try:
                    assert get_user_model().objects.create_user(names[i], 'account-{i}@local.host'.format(i=i), names[i])
                    created_count += 1
                except:
                    pass
