# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.uuid import UUID64Model


class TicketManager(models.Manager):
    """ Manager des tickets """

    # Getter
    def by_user(self, user):
        """ Renvoyer les tickets d'un utilisateur """
        return self.filter(author=user)

    def closed(self):
        """ Renvoyer les tickets fermés """
        return self.filter(closed=True)

    def open(self):
        """ Renvoyer les tickets ouverts """
        return self.filter(closed=False)

    def by_administrator(self, user):
        """ Renvoyer les tickets gérés par un utilisateur """
        return self.filter(administrators=user)


class Ticket(DatetimeModel, UUID64Model):
    """ Ticket """
    # Constantes
    RESOLUTIONS = [[0, _("New")], [1, _("New")], [2, _("New")], [3, _("New")], [4, _("New")], [5, _("Closed")]]
    CLOSING = {0: False, 1: False, 2: False, 3: False, 4: False, 5: True}
    NEW, CLOSED = 0, 5
    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="ticket_author", verbose_name=_("Author"))
    title = models.CharField(max_length=128, blank=False, verbose_name=_("Title"))
    description = models.TextField(validators=[MinLengthValidator(24)], verbose_name=_("Description"))
    closed = models.BooleanField(default=False, db_index=True, verbose_name=_("Closed"))
    updated = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_("Updated"))
    # Statut (à mettre à jour avec le dernier update)
    status = models.SmallIntegerField(default=0, db_index=True, verbose_name=_("Status"))
    related = models.ManyToManyField('ticket.Ticket', related_name='referenced_by', verbose_name=_("Related tickets"))
    # Administrateurs du ticket
    administrators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='tickets_managed', verbose_name=_("Administrators"))
    objects = TicketManager()

    # Getter
    def get_update_count(self):
        """ Renvoyer le nombre de mises à jour du ticket """
        from scoop.user.social.ticket.models import Update
        # Nombre d'updates
        return Update.objects.filter(ticket=self).count()

    def is_administrator(self, user):
        """ Renvoyer si un utilisateur administre le ticket """
        administrator = user in self.administrators
        superuser = user.is_superuser
        return administrator or superuser

    def get_updates(self):
        """ Renvoyer les mises à jour du ticket """
        from scoop.user.social.ticket.models import Update
        # Mises à jour
        return Update.objects.get_for_ticket(self)

    # Setter
    def update(self, status, body):
        """ Ajouter une mise à jour au ticket """
        from scoop.user.social.ticket.models import Update
        # Définir le statut
        Update.objects.create(ticket=self, status=status, body=body)
        self.status = status
        self.closed = Ticket.CLOSING[status]
        self.save(update_fields=['status', 'closed', 'updated'])

    def close(self, value=True):
        """ Fermer le ticket """
        if self.closed is not value:
            if value is True:
                self.status = Ticket.CLOSED
            self.closed = value
            self.save()

    # Overrides
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.title

    @permalink
    def get_aboslute_path(self):
        """ Renvoyer l'URL du ticket """
        return ('ticket:ticket-view', [self.uuid])

    # Métadonnées
    class Meta:
        verbose_name = _("ticket")
        verbose_name_plural = _("tickets")
        permissions = (('can_close_ticket', ugettext("Can close a ticket")),)
        app_label = 'ticket'
