# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField

from scoop.core.abstract.content.picture import PicturedModel
from scoop.core.abstract.core.birth import BirthManager, BirthModel
from scoop.core.abstract.core.uuid import UUID32Model
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.util.model.model import SingleDeleteManager


class PersonManager(SingleDeleteManager, BirthManager):
    """ Manager des personnes """

    # Getter
    def find_by_family_name(self, name):
        """ Renvoyer des personnes avec un nom de famille débutant par une expression """
        return self.filter(family_name__istartswith=name.strip())


class Person(PicturedModel, WeightedModel, BirthModel, UUID32Model):
    """ Personne """
    # Constantes
    TITLES = [['m', _(u"Mister")], ['mme', _(u"Miss'ess")], ['mlle', _(u"Miss")], ['dr', _(u"Doctor")]]
    # Champs
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='person', on_delete=models.SET_NULL, verbose_name=_(u"User"))
    full_name = models.CharField(max_length=64, blank=False, verbose_name=_(u"Full name"))
    prefix = models.CharField(max_length=4, blank=False, choices=TITLES, verbose_name=_(u"Prefix"))
    given_name = models.CharField(max_length=64, blank=True, verbose_name=_(u"Name given at birth"))
    additional_name = models.CharField(max_length=64, blank=True, verbose_name=_(u"Name given at birth"))
    family_name = models.CharField(max_length=64, blank=True, verbose_name=_(u"Family name"))
    nickname = models.CharField(max_length=32, blank=True, verbose_name=_(u"Nickname"))
    url = models.URLField(max_length=100, blank=True, verbose_name=_(u"Personal page"))
    email = models.EmailField(max_length=64, blank=True, verbose_name=_(u"Email"))
    telephone = models.CharField(max_length=128, blank=True, help_text=_(u"ex. Home:1114567, Fax:1114568, 1114569"), verbose_name=_(u"Phone numbers"))
    notes = models.TextField(blank=True, verbose_name=_(u"Additional notes"))
    # Lieu
    street_address = models.CharField(max_length=192, blank=True, help_text=_(u"Street number, name and appartment/suite"), verbose_name=_(u"Street address"))
    city = models.CharField(max_length=96, blank=True, verbose_name=_(u"City"))
    postal_code = models.CharField(max_length=24, blank=True, verbose_name=_(u"Postal code"))
    country = CountryField()
    objects = PersonManager()

    # Getter
    def get_telephone(self):
        """ Renvoyer la liste des numéros de téléphone """
        values = [text.strip() for text in self.telephone.split(',')]
        phones = list()
        for value in values:
            label, tel = value.split(':') if ':' in value else None, value
            phones.append([label, tel])
        return phones

    # Métadonnées
    class Meta:
        verbose_name = _(u"person")
        verbose_name_plural = _(u"persons")
        app_label = 'people'
