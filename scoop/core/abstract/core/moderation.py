# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ModeratedQuerySetMixin(object):
    """ Mixin de queryset pour les objets modérés """

    # Getter
    def moderated(self, **kwargs):
        """ Renvoyer les objets modérés """
        return self.filter(moderated=True, **kwargs)

    def pending(self, **kwargs):
        """ Renvoyer les objets en attente de modération """
        return self.filter(moderated__isnull=True, **kwargs)

    def unmoderated(self, **kwargs):
        """ Renvoyer les objets en attente de modération """
        return self.pending(**kwargs)

    def denied(self, **kwargs):
        """ Renvoyer les objets refusés """
        return self.filter(moderated=False, **kwargs)


class ModeratedModel(models.Model):
    """ Mixin de modèle modéré """
    # Constantes
    MODERATED_CHOICES = [[None, _("Pending")], [False, _("Refused")], [True, _("Accepted")]]

    # Champs
    moderated = models.NullBooleanField(default=None, choices=MODERATED_CHOICES, verbose_name=_("Moderated"))

    # Overrides
    def save(self, *args, **kwargs):
        """ Sauvegarder l'objet dans la base de données """
        if hasattr(self, 'author'):
            if self.author and self.author.is_staff:
                self.moderated = True
        super(ModeratedModel, self).save(*args, **kwargs)

    # Setter
    def moderate_auto(self, request=None):
        """ Modérer automatiquement l'objet """
        pass

    def moderate_accept(self, save=False):
        """ Accepter l'objet """
        if self.moderated is not True:
            self.moderated = True
            if save is True:
                super(ModeratedModel, self).save()

    def moderate_refuse(self, save=False):
        """ Refuser l'objet """
        if self.moderated is not False:
            self.moderated = False
            if save is True:
                super(ModeratedModel, self).save()

    def moderate_pending(self, save=False):
        """ Remettre l'objet en attente de modération """
        if self.moderated is not None:
            self.moderated = None
            if save is True:
                super(ModeratedModel, self).save()

    # Getter
    def get_moderation_status(self):
        """ Renvoyer le statut de modération de l'objet """
        return {None: _("pending"), False: _("denied"), True: _("accepted")}[self.moderated]

    # Métadonnées
    class Meta:
        abstract = True
