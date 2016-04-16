# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.shortcuts import addattr


class AcceptableModel(models.Model):
    """ Objet accepté, ex. bonne réponse """
    # Champs
    accepted = models.BooleanField(default=False, editable=False, verbose_name=_("Accepted"))

    # Getter
    @addattr(short_description=_("Accepted answer"))
    def is_accepted(self):
        """ Renvoyer si l'objet est la réponse acceptée """
        return self.accepted

    # Setter
    def accept(self, value=True):
        """ Accepter l'objet comme meilleure réponse à son contenu """
        if self.content_type and self.object_id and value is True and self.accepted is False:
            # - Trouver les commentaires avec la même cible et supprimer les accepted
            content_type, content_id = self.content_type, self.object_id
            self._meta.concrete_model.objects.filter(content_type=content_type, object_id=content_id).update(accepted=False)
            self.accepted = value
            self.save(update_fields=['accepted'])
        else:
            self.unaccept()

    def unaccept(self):
        """ Ne plus accepter l'objet comme meilleure réponse """
        if self.accepted is True:
            self.accepted = False
            self.save(update_fields=['accepted'])

    # Métadonnées
    class Meta:
        abstract = True
