# coding: utf-8
import logging

import pytz
from django.conf import settings
from django.db import models
from django.utils import timezone, translation
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.content.picture import PicturableModel
from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.location.coordinates import CoordinatesModel
from scoop.core.util.shortcuts import addattr
from scoop.location.util.country import get_country_icon_html
from unidecode import unidecode

logger = logging.getLogger(__name__)


class CountryQuerySet(models.QuerySet):
    """ Mixin de Queryset/Manager des pays """

    # Getter
    def get_by_natural_key(self, code2):
        """ Clé naturelle """
        return self.get(code2=code2)

    def public(self):
        """ Renvoyer les pays publics """
        return self.filter(public=True)

    def get_by_code2_or_none(self, code2):
        """ Renvoyer un pays selon son code ISO à 2 lettres """
        if self.filter(code2__iexact=code2).exists():
            return self.get(code2__iexact=code2)
        return None

    def by_codes(self, codes):
        """ Renvoyer des pays selon leur code ISO à 2 lettres """
        return self.filter(code2__in=codes)

    def by_continent_code(self, code):
        """ Renvoyer des pays par continent """
        return self.filter(continent__iexact=code)

    def is_safe(self, code2):
        """ Renvoyer si un pays portant un code est considéré sain """
        return code2 == "" or code2.lower() in settings.LOCATION_SAFE_COUNTRIES or self.filter(safe=True, code2__iexact=code2).exists()

    def are_safe(self, codes):
        """ Renvoyer si plusieurs pays sont sains """
        codes = {code.upper() for code in codes}
        return not codes or not self.filter(safe=False, code2__in=codes).exists()


class Country(CoordinatesModel, PicturableModel, DataModel):
    """ Pays """

    # Constantes
    DATA_KEYS = ['neighbours']
    CONTINENTS = [['AF', _("Africa")], ['AS', _("Asia")], ['EU', _("Europe")], ['NA', _("North America")],
                  ['OC', _("Oceania")], ['SA', _("South America")], ['AN', _("Antarctica")]]

    # Champs
    name = models.CharField(max_length=100, blank=False, verbose_name=_("Name"))
    code2 = models.CharField(max_length=2, unique=True, db_index=True, verbose_name=_("ISO Code"))
    code3 = models.CharField(max_length=3, unique=True, db_index=True, verbose_name=_("ISO Code 3"))
    phone = models.CharField(max_length=8, default="", blank=True, verbose_name=_("Phone prefix"))
    continent = models.CharField(max_length=2, choices=CONTINENTS, db_index=True, verbose_name=_("Continent"))
    population = models.IntegerField(default=0, verbose_name=_("Population"))
    area = models.FloatField(default=0, verbose_name=pgettext_lazy('country', "Area"))
    capital = models.CharField(max_length=96, blank=True, verbose_name=pgettext_lazy('country', "Capital"))
    currency = models.ForeignKey('location.Currency', null=True, blank=True, related_name='countries', verbose_name=_("Currency"))
    regional_level = models.SmallIntegerField(default=1, verbose_name=_("Regional level"))
    subregional_level = models.SmallIntegerField(default=2, verbose_name=_("Sub-regional level"))
    public = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('country', "Public"))  # accessible aux membres ?
    safe = models.BooleanField(default=False, verbose_name=pgettext_lazy('country', "Safe"))  # considéré par le site comme un pays autorisé ?
    updated = models.DateTimeField(default=timezone.now, verbose_name=pgettext_lazy('country', "Last update"))  # utilisé pour les différentiels de mises à jour
    objects = CountryQuerySet.as_manager()

    # Getter
    @addattr(admin_order_field='name', short_description=_("Name"))
    def get_name(self):
        """ Renvoyer le nom du pays """
        language = translation.get_language()
        names = self.alternates.filter(language=language).order_by('-preferred', '-short')
        if names.exists():
            return names[0].name
        return self.name

    def has_name(self, name):
        """ Renvoyer si le pays possède un nom """
        name = name.strip().lower()
        return self.name.lower() == name or self.alternates.filter(name__iexact=name).exclude(language__in=['link']).exists()

    @addattr(short_description=_("City count"))
    def get_entries_count(self):
        """ Renvoyer le nombre de villes dans le pays """
        return self.cities.filter(city=True).count()

    def has_entries(self):
        """ Renvoyer si le pays a au moins un élément City """
        from scoop.location.models import City
        # Tous les éléments City
        return City.objects.filter(country=self).exists()

    @addattr(allow_tags=True, admin_order_field='code2', short_description=_("Icon"))
    def get_icon(self, directory="png24"):
        """ Renvoyer une icône du pays """
        return get_country_icon_html(self.code2, self.get_name(), directory=directory)

    @addattr(admin_order_field='area', short_description=pgettext_lazy('country', "Area"))
    def get_area(self, unit=None):
        """ Renvoyer la superficie du pays, en m² ou en mi² """
        conversion = {None: 1.0, 'mi': 0.386102159}
        unit_name = {None: 'km²', 'mi': 'mi²'}
        return "{area:.0f} {unit}".format(area=self.area * conversion.get(unit, 1.0), unit=unit_name.get(unit, 'km²'))

    def get_timezones(self):
        """ Renvoyer les fuseaux horaires du pays """
        from scoop.location.models import Timezone
        # Trouver via Pytz
        names = pytz.country_timezones.get(self.code2, [])
        timezones = [Timezone.by_name(name) for name in names]
        return timezones

    def get_neighbours(self):
        """ Renvoyer les pays voisins """
        country_names = [name.upper().strip() for name in self.get_data('neighbours', '').split(',')]
        countries = Country.objects.filter(code2__in=country_names)
        return countries

    @staticmethod
    def by_code2(code):
        """ Renvoyer le pays correspondant au code ISO 2 lettres """
        return Country.objects.get_by_code2_or_none(code)

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.get_name()

    def __repr__(self):
        """ Renvoyer la représentation ASCII de l'objet """
        return unidecode(self.get_name())

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self.code2 = self.code2.upper()
        self.code3 = self.code3.upper()
        if self.latitude is None or self.longitude is None:
            self.latitude, self.longitude = 0.0, 0.0
        super(Country, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("country")
        verbose_name_plural = _("countries")
        app_label = 'location'


class CountryName(models.Model):
    """ Noms alternatifs de pays """

    # Champs
    id = models.IntegerField(primary_key=True, verbose_name=_("Alternate ID"))
    country = models.ForeignKey('location.Country', null=False, on_delete=models.CASCADE, related_name='alternates', verbose_name=_("Country"))
    language = models.CharField(max_length=10, blank=False, verbose_name=_("Language name"))
    name = models.CharField(max_length=200, blank=False, verbose_name=_("Name"))
    preferred = models.BooleanField(default=False, verbose_name=_("Preferred"))
    short = models.BooleanField(default=False, verbose_name=_("Short version"))

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _("Name for {country}/{lang}").format(country=self.country.name, lang=self.language)

    # Métadonnées
    class Meta:
        verbose_name = _("country name")
        verbose_name_plural = _("country names")
        index_together = [['country', 'language', 'preferred']]
        app_label = 'location'
