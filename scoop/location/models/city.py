# coding: utf-8
from __future__ import absolute_import

from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.measure import D
from django.core.cache import cache
from django.db import models
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.encoding import python_2_unicode_compatible
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from unidecode import unidecode

from scoop.core.abstract.content.picture import PicturableModel
from scoop.core.abstract.location.coordinates import CoordinatesModel
from scoop.core.util.data.typeutil import make_iterable
from scoop.core.util.model.model import search_query
from scoop.core.util.shortcuts import addattr
from scoop.core.util.stream.request import default_context
from scoop.location.util.gis import Distance
from scoop.location.util.weather import get_open_weather


class CityQuerySetMixin(object):
    """
    Mixin de Queryset/Manager des villes
    """

    # Getter
    def city(self):
        """
        Renvoyer les villes uniquement
        :type self: django.db.models.Manager
        """
        return self.filter(city=True)

    def by_level(self, country, level):
        """
        Renvoyer les éléments d'un niveau administratif
        :type self: django.db.models.Manager
        """
        return self.filter(country=country, level=level)

    def by_name(self, name, city=True, **kwargs):
        """
        Renvoyer les villes portant un nom
        :type self: django.db.models.Manager
        """
        fields = ['alternates__ascii', 'country__alternates__name']
        final_query = search_query(unidecode(name), fields, queryset=self.filter(city=city, **kwargs))
        return final_query.distinct().order_by('-population')

    def get_by_name(self, name, city=True, **kwargs):
        """ Renvoyer la ville la plus peuplée parmi celles portant un nom """
        cities = self.by_name(name, city, **kwargs)
        return cities.first()

    def by_population(self, country_codes, value, operator=">="):
        """
        Renvoyer les villes correspondant à un critère sur leur population
        :type self: django.db.models.Manager
        :param country_codes: liste de codes pays pour lesquels filtrer
        :param value: nombre d'habitants
        :param operator: modifie la sélection par rapport à un nombre d'habitants
            opérateur entre =, <, >, <= et >=
        """
        OPS = {'=': 'exact', '<': 'lt', '<=': 'lte', '>': 'gt', '>=': 'gte'}
        criteria = {'population__{operator}'.format(operator=OPS.get(operator, 'gte')): value}
        return self.filter(country__code2__in=make_iterable(country_codes, list), **criteria)

    def by_country(self, country):
        """
        Renvoyer les éléments dans un pays
        :type self: django.db.models.Manager
        """
        return self.filter(country__code2__iexact=country) if isinstance(country, str) else self.filter(country__id=country.id)

    def in_box(self, box):
        """
        Renvoyer les villes uniquement situées dans un rectangle
        :type self: django.db.models.Manager
        """
        polygon = Polygon.from_bbox([box[1], box[0], box[3], box[2]])
        return self.filter(position__contained=polygon, city=True)

    def in_square(self, point, km):
        """ Renvoyer les villes uniquement dans un carré avec un centre et une longueur de demi-diagonale """
        return self.in_box(City.get_bounding_box_at(point, km))

    def in_radius(self, point, km):
        """
        Renvoyer les villes uniquement dans un cercle de n km autour d'un point
        :type self: django.db.models.Manager
        """
        center = Point(point[1], point[0])
        return self.filter(position__distance_lt=(center, D(km=km)))

    def biggest(self, point, km=20):
        """ Renvoyer la ville la plus peuplée à n km autour d'un point """
        cities = self.in_radius(point, km).order_by('-population')
        return cities.first() if cities.exists() else None

    def find_by_name(self, point, name):
        """
        Renvoyer une ville la plus proche d'un point, portant un nom si possible
        :type self: django.db.models.Manager, CityQuerySetMixin
        """
        name = unidecode(name).lower().strip() if name else '*'
        # Renvoyer le résultat en cache
        CACHE_KEY = "location.city.find:{lat:.2f}:{lon:.2f}:{name}".format(lat=point[0], lon=point[1], name=name or '*')
        result = cache.get(CACHE_KEY, None)
        if result is not None:
            return self.get(id=result)
        # Ou retrouver la ville la plus proche
        cities = self.filter(city=True, alternates__ascii=name).in_square(point, 128).distinct()  # recherche par cityname.ascii -> 128km
        cities = cities if cities.exists() else self.filter(city=True, ascii=name).in_square(point, 128).distinct()  # recherche par city.ascii -> 128km
        cities = cities if cities.exists() else self.filter(city=True).in_square(point, 8)  # recherche par lat/lon -> 8km
        if cities.exists():
            cities = cities.annotate(distance=Distance('position', Point(point[1], point[0], srid=4326))).order_by('distance')
            closest_city = cities.first()
            cache.set(CACHE_KEY, closest_city.pk)
            return closest_city
        return None


class CityQuerySet(models.QuerySet, CityQuerySetMixin):
    """ Queryset des villes """
    pass


class CityManager(models.Manager.from_queryset(CityQuerySet), models.Manager, CityQuerySetMixin):
    """ Manager des villes """
    pass


class City(CoordinatesModel, PicturableModel):
    """ Villes, communes, etc. """

    # Constantes
    LOOKUP_CACHE_TIMEOUT = 1800

    # Champs
    id = models.IntegerField(primary_key=True, null=False, verbose_name=_("Geonames ID"))
    city = models.BooleanField(default=False, db_index=True, verbose_name=_("City?"))
    type = models.CharField(max_length=8, verbose_name=_("Type"))
    feature = models.CharField(max_length=1, verbose_name=_("Feature"))
    a1 = models.CharField(max_length=16, blank=True, verbose_name="A1")
    a2 = models.CharField(max_length=16, blank=True, verbose_name="A2")
    a3 = models.CharField(max_length=16, blank=True, verbose_name="A3")
    a4 = models.CharField(max_length=16, blank=True, verbose_name="A4")
    country = models.ForeignKey('location.Country', null=False, related_name='cities', verbose_name=_("Country"))
    name = models.CharField(max_length=200, blank=False, verbose_name=_("Name"))
    ascii = models.CharField(max_length=200, db_index=True, blank=False, verbose_name=_("ASCII"))
    code = models.CharField(max_length=32, blank=True, verbose_name=_("Code"))
    population = models.IntegerField(default=0, db_index=True, verbose_name=_("Population"))
    timezone = models.ForeignKey('location.Timezone', null=True, db_index=False, related_name='cities', verbose_name=_("Timezone"))
    level = models.SmallIntegerField(default=0, verbose_name=_("Level"))
    parent = models.ForeignKey('self', null=True, related_name='children', verbose_name=_("Parent"))
    objects = CityManager()

    # Getter
    @staticmethod
    def named(name):
        """ Renvoyer une ville nommée *name* """
        return City.objects.city().get_by_name(name)

    def get_children(self, city_only=False):
        """ Renvoyer les villes enfants directs """
        criteria = {'city': True} if city_only else {}
        return City.objects.filter(parent=self, **criteria)

    def get_siblings(self, **kwargs):
        """ Renvoyer les villes avec le même parent """
        return City.objects.filter(parent=self.parent, country=self.country, type=self.type, **kwargs).exclude(pk=self.pk)

    def get_with_common_ancestor(self, level=None, city_only=True):
        """ Renvoyer les villes avec le même parent de niveau n """
        level = self.country.subregional_level if level is None else level
        level = self.level if (level > self.level and self.level >= 1) else level
        criteria = {'a{}'.format(idx): getattr(self, 'a{}'.format(idx)) for idx in range(1, level + 1)}
        if city_only is True:
            criteria['city'] = True
        return City.objects.filter(country=self.country, **criteria)

    def get_formatted_text(self):
        """ Renvoyer la représentation texte de l'objet """
        return _("{city}, {parent}, {country}").format(city=self.get_name(), parent=self.get_auto_parent(), country=self.country)

    def get_auto_parent(self, level=None):
        """ Renvoyer l'élément parent le plus pertinent selon le pays """
        from scoop.location.models import Country
        # Pas de parent direct, renvoyer immédiatement le pays
        if self.parent_id is None:
            return self.country
        # Rechercher un résultat en cache
        CACHE_KEY = "location.city.ap:{id}".format(id=self.id)
        result = cache.get(CACHE_KEY, None)
        if result is not None:
            parent = City.objects.filter(id=result) or Country.objects.filter(id=result)  # On a en cache soit un id de ville soit de pays
            return parent.first()
        # Autrement parcourir les parents jusqu'au level désiré
        level = self.country.subregional_level if level is None else level
        parent = self.parent
        while parent and getattr(parent, 'level', 0) >= level:
            parent = parent.parent
        # Si parent non trouvé, renvoyer le pays. Sinon mettre en cache
        if parent is None:
            parent = self.country
        cache.set(CACHE_KEY, parent.pk, City.LOOKUP_CACHE_TIMEOUT)  # parent peut être None
        return parent

    def get_close_cities(self, km, circle=False):
        """ Renvoyer les villes les plus proches à n km """
        cities = City.objects.in_radius(self.get_point(), km).filter(city=True)
        return cities

    def get_biggest_close_city(self, km=30):
        """ Renvoyer la ville la plus proche dans les n km """
        return City.objects.biggest(self.get_point(), km)

    def get_weather_forecast(self):
        """ Renvoyer la prévision météo de la ville """
        return get_open_weather(location=self)

    def render_weather_forecast(self):
        """ Rendre les prévisions météo de la ville """
        forecast = self.get_weather_forecast()
        output = render_to_string('location/display/forecast.html', {'forecast': forecast, 'city': self}, default_context())
        return mark_safe(output)

    @addattr(allow_tags=True, admin_order_field='country__code2', short_description=_("Icon"))
    def get_country_icon(self, directory="png24"):
        """ Renvoyer une icône du pays de la ville """
        return self.country.get_icon(directory=directory)

    def fetch_picture(self, force=False, count=4):
        """ Récupérer automatiquement des images pour la ville """
        from scoop.user.models import User
        # Expressions de recherche
        default = "{code} {name}".format(type=_("city"), name=self.get_name(), code=self.code, country=self.country)
        fallback = "{name}".format(name=self.get_name())
        return self._fetch_pictures(default, fallback, count, User.objects.get_superuser(), force)

    @addattr(short_description=_("Tree"))
    def get_tree(self, depth=4):
        """ Renvoyer une liste de l'arborescence de la ville """
        city_list = [self]
        city = self.parent
        while city is not None and depth > 0:
            city_list.append(city)
            city = city.parent if city.parent != city else None
            depth -= 1
        city_list.append(self.country)
        city_list.reverse()
        return city_list

    @addattr(short_description=_("Formatted tree"))
    def get_path(self):
        """ Renvoyer la représentation texte de l'arborescence de la ville """
        city_tree = self.get_tree()
        output = render_to_string("location/format/tree.html", {'tree': city_tree})
        return output

    @addattr(admin_order_field='name', short_description=_("Name"))
    def get_name(self, language=None):
        """ Renvoyer le nom de la ville """
        language = language or (translation.get_language() or 'en')[0:2]
        names = self.alternates.filter(language__in=[language, '']).order_by('-preferred', '-short')
        if names.exists():
            return names[0].name
        return self.name

    def has_name(self, name):
        """ Renvoyer si la ville porte un nom """
        name = name.strip().lower()
        return self.name.lower() == name or self.alternates.filter(name__iexact=name).exclude(language__in=['post', 'link']).exists()

    @addattr(short_description=_("Code"))
    def get_code(self):
        """ Renvoyer le code postal par défaut de la ville """
        names = self.alternates.filter(language='post').order_by('-preferred', '-short', 'name')
        if names.exists() and not self.code:
            self.code = names[0].name
            self.save()
        return self.code

    def get_codes(self):
        """ Renvoyer tous les codes postaux de la ville """
        return self.alternates.filter(language='post').order_by('-preferred', 'name').values_list('name', flat=True)

    def has_code(self, code):
        """ Renvoyer si un code postal appartient à la ville """
        return code in self.get_codes()

    # Overrides
    @python_2_unicode_compatible
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return "{name}".format(name=self.get_name(), country=self.country.code2)

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(City, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("city")
        verbose_name_plural = _("cities")
        index_together = [['a1', 'a2', 'a3', 'a4']]
        app_label = 'location'
        abstract = False


class CityName(models.Model):
    """ Nom alternatif de ville """
    # Champs
    id = models.IntegerField(primary_key=True, verbose_name=_("Alternate ID"))
    city = models.ForeignKey('location.City', null=False, on_delete=models.CASCADE, related_name='alternates', verbose_name=_("City"))
    language = models.CharField(max_length=10, blank=True, verbose_name=_("Language name"))
    name = models.CharField(max_length=200, blank=False, verbose_name=_("Name"))
    ascii = models.CharField(max_length=200, db_index=True, blank=False, verbose_name=_("Name"))
    preferred = models.BooleanField(default=False, verbose_name=_("Preferred"))
    short = models.BooleanField(default=False, verbose_name=_("Short version"))

    # Getter
    def _asciize(self):
        """ Générer une version ascii du nom de ville """
        ascii_version = unidecode(self.name).lower()
        if self.ascii != ascii_version:
            self.ascii = ascii_version
            return True
        return False

    # Setter
    def set_name(self, name):
        """ Définir le nom de ville """
        self.name = name
        if self._asciize() is True:
            self.save(update_fields=['name', 'ascii'])

    # Overrides
    @python_2_unicode_compatible
    def __str__(self):
        """ Renvoyer une représentation unicode de l'objet """
        return _("Name for {}").format(self.city.ascii)

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self._asciize()
        super(CityName, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("city name")
        verbose_name_plural = _("city names")
        index_together = [['city', 'language', 'preferred']]
        app_label = 'location'
        abstract = False
