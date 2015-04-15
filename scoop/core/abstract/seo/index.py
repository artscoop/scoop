# coding: utf-8
from __future__ import absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.shortcuts import addattr
from scoop.core.util.signals import check_indexable


class SEIndexQuerySetMixin(object):
    """ Mixin de queryset des objets indexables """

    # Getter
    def se_indexed(self, **kwargs):
        """ Renvoyer les objets indexables """
        return self.filter(se_indexed=True, **kwargs)

    def se_deindexed(self, **kwargs):
        """ Renvoyer les objets non indexables """
        return self.filter(se_indexed=False, **kwargs)


# ===============================================================================
# Classe de base pour les objets qui peuvent être indexés ou non par un moteur
# (via la balise HTML "meta robots")
# ===============================================================================
class SEIndexModel(models.Model):
    """ Mixin de modèle dont on peut choisir l'indexation dans les moteurs de recherche """
    se_indexed = models.BooleanField(default=False, null=False, db_index=True, verbose_name=_(u"Index in search engines"))

    # Getter
    @addattr(boolean=True, short_description=_(u"Index/Follow"))
    def _update_se_indexed(self):
        """ Mettre à jour l'état indexable automatiquement """
        result = check_indexable.send(self._meta.model, instance=self)
        valid = [item for item in result if item[1] is True]
        self.se_indexed = any(valid)
        return self.se_indexed

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self._update_se_indexed()
        super(SEIndexModel, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        abstract = True
