# coding: utf-8
from __future__ import absolute_import
from django.db import models
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.data import DataModel


class ApprovalModel(DataModel):
    """ Mixin de modèle modéré avec conservation de l'état non approuvé """
    approved = models.NullBooleanField(default=None, verbose_name=_(u"Approved"))

    # Overrides
    def save(self, *args, **kwargs):
        """ Sauvegarder l'objet dans la base de données """
        if hasattr(self, 'author'):
            if self.author and self.author.is_staff:
                self.approved = True
        super(ModeratedModel, self).save(*args, **kwargs)

    # Setter
    def moderate_auto(self, request=None):
        """ Modérer automatiquement l'objet """
        pass

    def moderate_accept(self, save=False):
        """ Accepter l'objet """
        if self.approved is not True:
            self.approved = True
            if save is True:
                super(ModeratedModel, self).save()

    def moderate_refuse(self, save=False):
        """ Refuser l'objet """
        if self.approved is not False:
            self.approved = False
            if save is True:
                super(ModeratedModel, self).save()

    def moderate_pending(self, save=False):
        """ Remettre l'objet en attente de modération """
        if self.approved is not None:
            self.approved = None
            if save is True:
                super(ModeratedModel, self).save()

    # Getter
    def get_moderation_status(self):
        """ Renvoyer le statut de modération de l'objet """
        return {None: _(u"pending"), False: _(u"denied"), True: _(u"accepted")}[self.approved]

    # Métadonnées
    class Meta:
        abstract = True
        fields = []
