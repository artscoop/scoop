# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.user.authored import AuthoredModel
from scoop.core.util.model.model import SingleDeleteManager


class UpdateManager(SingleDeleteManager):
    """ Manager des mises à jour de tickets """

    # Getter
    def get_for_ticket(self, ticket):
        """ Renvoyer les mises à jour pour un ticket """
        updates = self.filter(ticket=ticket).order_by('-id')
        return updates


class Update(AuthoredModel, DatetimeModel):
    """ Mise à jour d'un ticket """
    # Champs
    ticket = models.ForeignKey('ticket.Ticket', related_name='updates', verbose_name=_("Ticket"))
    status = models.ForeignKey('ticket.Resolution', related_name='updates+', verbose_name=_("Status"))
    body = models.TextField(blank=True, verbose_name=_("Body"))
    objects = UpdateManager()

    # Métadonnées
    class Meta:
        verbose_name = _("ticket update")
        verbose_name_plural = _("ticket updates")
        app_label = 'ticket'
