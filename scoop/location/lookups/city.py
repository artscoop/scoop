# coding: utf-8
from ajax_select import LookupChannel
from django.core.cache import cache
from django.db import models
from scoop.core.util.model.model import search_query
from scoop.location.models.city import City
from unidecode import unidecode


class CityLookup(LookupChannel):
    """ Lookup ajax-select des villes """

    model = City
    plugin_options = {'minLength': 2, 'delay': 500, 'position': {"my": "left bottom", "at": "left top", "collision": "flip"}}

    # Constantes
    CACHE_KEY = 'lookup.city.{}'

    # Getter
    def get_query(self, q, request):
        """ Renvoyer les villes correspondant à la requête """
        items_cache = cache.get(self.CACHE_KEY.format(q), None)
        if items_cache is not None:
            return items_cache
        fields = ['alternates__ascii', 'parent__parent__alternates__ascii']
        final_query = search_query(unidecode(q), fields)
        final_query = models.Q(city=True) & final_query
        items = City.objects.filter(final_query).distinct().order_by('-population')[0:12]
        cache.set(self.CACHE_KEY.format(q), items, 1800)
        return items

    def get_result(self, obj):
        """ Renvoyer la représentation texte de l'objet """
        return "{code} {name}, {parent}, {country}".format(code=obj.get_code(), name=obj.get_name(), country=obj.country, parent=obj.get_auto_parent())

    def format_match(self, obj):
        """ Renvoyer la représentation HTML de l'objet dans le dropdown """
        output = "{icon} <span class='muted'>{code}</span> <strong>{name}</strong>".format(icon=obj.country.get_icon(), name=obj.get_name(),
                                                                                           code=obj.get_code())
        return output

    def format_item_display(self, obj):
        """ Renvoyer la représentation HTML de l'objet dans le deck """
        output = "<span class='text-middle'>{country} <span class='muted'>{code}</span> <strong>{name}</strong></span><br>{parent}".format(name=obj.get_name(),
                                                                                                                                           country=obj.get_country_icon(
                                                                                                                                               directory="png"),
                                                                                                                                           code=obj.get_code(),
                                                                                                                                           parent=obj.get_auto_parent())
        return output

    def check_auth(self, request):
        """ Renvoyer si l'utilisateur peut envoyer une requête """
        return True


class CityPublicLookup(CityLookup):
    """ Lookup ajax-select des villes, pays publics uniquement """
    # Constantes
    CACHE_KEY = 'lookup.cityp.{}'

    # Getter
    def get_query(self, q, request):
        """ Renvoyer les villes correspondant à la requête """
        items_cache = cache.get(self.CACHE_KEY.format(q), None)
        if items_cache:
            return items_cache
        fields = ['alternates__ascii', 'ascii', 'parent__parent__alternates__ascii']
        final_query = search_query(unidecode(q), fields)
        final_query = models.Q(city=True, country__public=True) & final_query
        items = City.objects.filter(final_query).distinct('id').order_by('-population')[0:12]
        cache.set(self.CACHE_KEY.format(q), items, 1800)
        return items


class CityPublicMinimalLookup(CityLookup):
    """ Lookup ajax-select des villes, simple """
    # Constantes
    CACHE_KEY = 'lookup.citypm.{}'

    # Getter
    def get_query(self, q, request):
        """ Renvoyer les villes correspondant à la requête """
        q = unidecode(q).strip().lower()
        items_cache = cache.get(self.CACHE_KEY.format(q), None)
        if items_cache is not None:
            return items_cache
        fields = ['alternates__ascii', 'country__code2']
        final_query = search_query(q, fields)
        final_query = models.Q(city=True, country__public=True) & final_query
        items = City.objects.filter(final_query).distinct().order_by('-population')[0:10]
        cache.set(self.CACHE_KEY.format(q), list(items), 1800)
        return items

    def format_item_display(self, obj):
        """ Renvoyer la représentation HTML de l'objet dans le deck """
        output = """{country} <span class="city-code">{code}</span> <span class="city-name">{name}</span> <span class="city-parent">{parent}</span>""".format(
                name=obj.get_name(), country=obj.get_country_icon(directory="png"), code=obj.get_code(), parent=obj.get_auto_parent())
        return output


class CityA1Lookup(CityLookup):
    """ Lookup ajax-select des villes, ADM1 uniquement """
    plugin_options = {'minLength': 3, 'delay': 250, 'position': {"my": "left bottom", "at": "left top", "collision": "flip"}}
    # Constantes
    CACHE_KEY = 'lookup.citya1.{}'

    # Getter
    def get_query(self, q, request):
        """ Renvoyer les villes correspondant à la requête """
        q = unidecode(q).strip().lower()
        items_cache = cache.get(self.CACHE_KEY.format(q), None)
        if items_cache is not None:
            return items_cache
        fields = ['alternates__ascii', 'ascii']
        final_query = search_query(q, fields)
        final_query = models.Q(city=False, type="ADM1") & final_query
        items = City.objects.filter(final_query).distinct().order_by('-population')[0:10]
        cache.set(self.CACHE_KEY.format(q), items, 1800)
        return items

    def format_item_display(self, obj):
        """ Renvoyer la représentation HTML de l'objet dans le deck """
        output = """{country} {name}""".format(name=obj.get_name(), country=obj.get_country_icon(directory="png"))
        return output
