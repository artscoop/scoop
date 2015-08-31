# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from unidecode import unidecode

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.util.model.model import SingleDeleteManager
from scoop.messaging.util.signals import negotiation_accepted, negotiation_denied, negotiation_sent


class NegotiationManager(SingleDeleteManager):
    """ Manager des négociations """

    # Getter
    def has_negotiation(self, source, target):
        """ Renvoyer si une négociation existe d'un utilisateur vers un autre """
        return self.filter(source=source, target=target).exists() or self.filter(source=target, target=source).exists()

    def get_negotiation(self, source, target):
        """ Renvoyer la négociation d'une source à une cible """
        if self.filter(source=source, target=target).exists():
            return self.get(source=source, target=target)
        return None

    def negotiations_for(self, target, **kwargs):
        """ Renvoyer toutes les négociations vers une cible """
        return self.filter(target=target, **kwargs)

    def accepted(self, target):
        """ Renvoyer les négociations acceptées par une cible """
        return self.filter(target=target, status=Negotiation.ACCEPTED)

    def pending(self, target):
        """ Renvoyer les négociations en attente vers une cible """
        return self.filter(target=target, status=Negotiation.PENDING)

    # Setter
    def negotiate(self, source, target):
        """ Créer une négociation entre source et cible """
        negotiation, created = self.get_or_create(source=source, target=target)
        if created is True:
            negotiation_sent.send(None, source=source, target=target)
        return negotiation

    def accept(self, source, target):
        """ Accepter une négociation entre source et cible """
        negotiation = self.get_negotiation(source, target)
        return negotiation.accept() if negotiation else None

    def deny(self, source, target):
        """ Refuser une négociation entre source et cible """
        negotiation = self.get_negotiation(source, target)
        return negotiation.deny() if negotiation else None


class Negotiation(DatetimeModel):
    """ Négociation d'autorisation d'envoeyer un message """
    # Constantes
    STATUS = [[None, _("Pending")], [True, _("Accepted")], [False, _("Denied")]]
    PENDING, ACCEPTED, DENIED = None, True, False
    # Champs
    source = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE, related_name="negotiations_made", verbose_name=_("Asker"))
    target = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE, related_name="negotiations_received", verbose_name=_("Target"))
    status = models.NullBooleanField(default=PENDING, db_index=True, verbose_name=_("Status"))
    thread = models.ForeignKey('messaging.Thread', null=True, on_delete=models.SET_NULL, verbose_name=_("Thread"))
    closed = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('negotiation', "Closed"))
    updated = models.DateTimeField(default=timezone.now, verbose_name=pgettext_lazy('negotiation', "Updated"))
    objects = NegotiationManager()

    # Setter
    def accept(self):
        """ Accepter la négociation """
        if not self.status == self.ACCEPTED:
            self.status = self.ACCEPTED
            self.closed = True
            self.save()
            return negotiation_accepted.send(self, source=self.source, target=self.target)
        return None

    def deny(self):
        """ Refuser la négociation """
        if not self.status == self.DENIED:
            self.status = self.DENIED
            self.closed = True
            self.save()
            negotiation_denied.send(self, source=self.source, target=self.target)
        return None

    # Overrides
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _("Messaging negotiation between {source} and {target}").format(source=self.source, target=self.target)

    def __repr__(self):
        """ Renvoyer la représentation texte de l'objet """
        return "Negotiation: {source}->{target}".format(source=unidecode(self.source), target=unidecode(self.target))

    # Métadonnées
    class Meta:
        unique_together = (('source', 'target'),)
        verbose_name = _("negotiation")
        verbose_name_plural = _("negotiations")
        app_label = "messaging"
