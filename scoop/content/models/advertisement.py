# coding: utf-8
from __future__ import absolute_import

import random

from django.db import models
from django.db.models.aggregates import Sum
from django.template.base import Template
from django.template.context import RequestContext
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.icon import IconModel
from scoop.core.abstract.core.rectangle import RectangleModel
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.abstract.user.authored import AuthoredModel
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.stream.request import default_request


class AdvertisementManager(SingleDeleteManager):
    """ Manager des annonces publicitaires """

    def get_by_name(self, name):
        """ Renvoyer une annonce selon son nom """
        try:
            return self.get(name__iexact=name)
        except:
            return None

    def by_group(self, group):
        """ Renvoyer des annonces d'un groupe """
        return self.filter(group__iregex=r"[^\|]{}\|?".format(group))

    def by_network(self, network):
        """ Renvoyer des annonces d'un réseau d'annonceurs """
        return self.filter(network__iexact=network)

    def random_by_size(self, width, height):
        """ Renvoyer une annonce aléatoire de la dimension indiquée """
        candidates = self.filter(width=width, height=height).order_by('?')
        return candidates[0] if candidates.exists() else None

    def random(self, group=None, **kwargs):
        """
        Renvoyer une annonce au hasard dans un groupe
        La probabilité qu'une annonce soit choisie augmente avec son poids
        """
        # Récupérer les annonces à afficher
        kwargs.update({'group__iregex': r"\|?{}\|?".format(group)} if group is not None else {})
        population = self.filter(active=True, weight__gt=0, width__gt=0, **kwargs)
        # Calculer le poids total de ces annonces
        total = population.aggregate(total_weight=Sum('weight'))['total_weight']
        # Choisir un nombre au hasard entre 0 et le poids des annonces
        cursor, position = 0, random.uniform(0, total)
        for item in population:
            cursor += item.weight
            if cursor >= position:
                return item
        # Population vide ou annonces avec des poids nuls : renvoyer None
        return None


class Advertisement(WeightedModel, DatetimeModel, AuthoredModel, IconModel, RectangleModel):
    """ Annonce publicitaire """

    # Constantes
    NETWORKS = [['gg', "Google Adsense"], ['af', "AdFever"], ['na', _("Custom")], ['ot', pgettext_lazy('adnetwork', "Other")]]
    # Champs
    name = models.CharField(max_length=32, unique=True, blank=False, verbose_name=_("Name"))
    active = models.BooleanField(default=True, blank=True, verbose_name=pgettext_lazy('advertisement', "Active"))
    group = models.CharField(max_length=48, blank=True, help_text=_("Pipe separated"), verbose_name=_("Group name"))
    code = models.TextField(blank=False, help_text=_("Django template code for HTML/JS"), verbose_name=_("HTML/JS Snippet"))
    views = models.IntegerField(default=0, editable=False, verbose_name=_("Views"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    network = models.CharField(choices=NETWORKS, default='na', max_length=4, db_index=True, verbose_name=_("Ad network"))
    objects = AdvertisementManager()

    def render(self, view=True):
        """ Effectuer le rendu de l'annonce """
        template = Template(self.code)
        context = RequestContext(default_request())
        context.update({'ad': self})
        # Incrémenter le compteur d'affichages
        if view is True:
            self.views += 1
            self.save(update_fields=['views'])
        return template.render(context)

    @python_2_unicode_compatible
    def __str__(self):
        """ Renvoyer auformat unicode """
        return _("Advertisement {name}").format(name=self.name)

    def save(self, *args, **kwargs):
        """ Sauvegarder l'objet dans la base de données """
        super(Advertisement, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("advertisement")
        verbose_name_plural = _("advertisements")
        app_label = 'content'
