# coding: utf-8
import random

from django.db import models
from django.db.models.aggregates import Sum
from django.template.base import Template
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.icon import IconModel
from scoop.core.abstract.core.rectangle import RectangleModel
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.abstract.user.authored import AuthoredModel
from scoop.core.util.model.model import SingleDeleteManager, SingleDeleteQuerySetMixin


class AdvertisementQuerySet(models.QuerySet, SingleDeleteQuerySetMixin):
    """ Manager des annonces publicitaires """

    # Getter
    def get_by_name(self, name):
        """ Renvoyer une annonce selon son nom """
        try:
            return self.get(name__iexact=name)
        except (Advertisement.DoesNotExist, Advertisement.MultipleObjectsReturned):
            return None

    def by_group(self, group):
        """ Renvoyer des annonces d'un groupe """
        return self.filter(group__iregex=r'[^\|]{}\|?'.format(group))

    def by_network(self, network):
        """ Renvoyer des annonces d'un réseau d'annonceurs """
        return self.filter(network__iexact=network)

    def by_keyword(self, keyword):
        """ Renvoyer des annonces avec un mot clé """
        return self.filter(keywords__icontains=keyword)

    def random_by_size(self, width, height):
        """ Renvoyer une annonce aléatoire de la dimension indiquée """
        candidates = self.filter(width=width, height=height).order_by('?')
        return candidates[0] if candidates.exists() else None

    def random_by_max_size(self, width, height):
        """ Renvoyer une annonce aléatoire de la dimension indiquée """
        candidates = self.filter(width__lte=width, height__lte=height).order_by('?')
        return candidates[0] if candidates.exists() else None

    def random(self, group=None, **kwargs):
        """
        Renvoyer une annonce au hasard dans un groupe

        La probabilité qu'une annonce soit choisie augmente avec son poids
        """
        # Récupérer les annonces à afficher
        kwargs.update({'group__iregex': r'\|?{}\|?'.format(group)} if group is not None else {})
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

    def select_ad(self, group=None, name=None, size=None):
        """ Renvoyer une annonce selon des critères de recherche """
        if group is None and name is None and size is None:
            return _("[group/name missing]")
        if group is not None:
            return self.random(group)
        elif name is not None:
            return self.get_by_name(name)
        elif size is not None:
            width, height = [int(item) for item in size.split('x')]
            return self.random_by_size(width, height)
        else:
            return None

    # Overrides
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Advertisement(WeightedModel, DatetimeModel, AuthoredModel, IconModel, RectangleModel):
    """ Annonce publicitaire """

    # Constantes
    NETWORKS = [['google-adsense', "Google Adsense"], ['miscellaneous', pgettext_lazy('adnetwork', "Other")]]

    # Champs
    name = models.CharField(max_length=32, unique=True, blank=False, verbose_name=_("Name"))
    active = models.BooleanField(default=True, blank=True, verbose_name=pgettext_lazy('advertisement', "Active"))
    group = models.CharField(max_length=48, blank=True, help_text=_("Pipe separated"), verbose_name=_("Group name"))
    code = models.TextField(blank=False, help_text=_("Django template code for HTML/JS"), verbose_name=_("HTML/JS Snippet"))
    views = models.IntegerField(default=0, editable=False, verbose_name=_("Views"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    keywords = models.CharField(max_length=128, blank=True, verbose_name=_("Keywords"))
    network = models.CharField(choices=NETWORKS, default='na', max_length=24, db_index=True, verbose_name=_("Ad network"))
    updated = models.DateTimeField(auto_now=True, verbose_name=pgettext_lazy('advertisement', "Updated"))
    objects = AdvertisementQuerySet.as_manager()

    # Getter
    def render(self, request, view=True):
        """
        Effectuer le rendu de l'annonce

        Si l'utilisateur a les permissions de cacher l'annonce,
        afficher un placeholders uniquement si l'utilisateur est du staff.

        :param view: si True, le rendu compte pour un affichage de l'annonce
        :param request: requête
        :type view: bool
        """
        template = Template(self.code)
        context = RequestContext(request)
        context.update({'ad': self})
        if not request.user.has_perm('content.can_hide_advertisement'):
            # Incrémenter le compteur d'affichages
            if view is True:
                self.views += 1
                self.save(update_fields=['views'])
            return template.render(context)
        else:
            if request.user.is_staff:
                return "{w}x{h} ad".format(w=self.width, h=self.height)
            return ""

    # Overrides
    def __str__(self):
        """ Renvoyer auformat unicode """
        return _("Advertisement {name}").format(name=self.name)

    def save(self, *args, **kwargs):
        """ Sauvegarder l'objet dans la base de données """
        super(Advertisement, self).save(*args, **kwargs)

    def natural_key(self):
        """ Clé naturelle """
        return self.name,

    # Métadonnées
    class Meta:
        verbose_name = _("advertisement")
        verbose_name_plural = _("advertisements")
        permissions = [('can_hide_advertisements', "Can hide advertisements")]
        app_label = 'content'
