# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy

from scoop.core.abstract.core.datetime import DatetimeModel


def get_default_expiry(self):
    """ Renvoyer la date d'expiration par défaut """
    return self.make_expiry(days=2, timestamp=False)


class SanctionManager(models.Manager):
    """ Manager des sanctions """

    # Getter
    def has_sanction(self, user):
        """ Renvoyer si un utilisateur est sanctionné """
        return user.sanctions.exists()


class Sanction(DatetimeModel):
    """ Sanction utilisateur """
    # Constantes
    TYPES = [[0, _("Posting disabled")], [1, _("Reading disabled")]]
    DURATIONS = [[7200, _("2 hours")], [86400, _("1 day")], [86400 * 3, _("3 days")], [86400 * 7, _("1 week")]]

    # Champs
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE, related_name='sanctions', verbose_name=_("User"))
    type = models.SmallIntegerField(default=0, choices=TYPES, db_index=True, verbose_name=_("Type"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    expires = models.DateTimeField(default=get_default_expiry, verbose_name=_("Expiry"))
    revoked = models.BooleanField(default=False, verbose_name=pgettext_lazy('sanction', "Revoked"))
    objects = SanctionManager()

    # Getter
    def is_active(self):
        """ Renvoyer si la sanction est active """
        return self.revoked is False and self.expires > timezone.now()

    # Overrides
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return "sanction on {user}: {type}".format(user=self.user, type=self.get_type_display())

    # Métadonnées
    class Meta:
        app_label = 'forum'
        verbose_name = _("sanction")
        verbose_name_plural = _("sanctions")
