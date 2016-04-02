# coding: utf-8
import datetime

import requests
from django.conf import settings

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.template.defaultfilters import slugify
from scoop.core.abstract.location.coordinates import CoordinatesModel


def get_open_weather(location, days=5, skip_cache=False):
    """ Renvoyer les données de météo OpenWeatherMap 2.0 """
    if not getattr(settings, 'OPENWEATHERMAP_API_KEY', False):
        raise ImproperlyConfigured("You must define an OPENWEATHERMAP_API_KEY in your settings before making a query.")
    if isinstance(location, CoordinatesModel) and isinstance(days, (int, float)):
        # Récupérer la météo en cache si possible
        cache_key = "location.weather.{type}.{id}.{days}".format(type=slugify(location._meta.object_name), id=location.pk, days=days)
        cached = cache.get(cache_key, None)
        if cached is not None and not skip_cache:
            return cached
        # Appeler l'API de Open Weather Map et récupérer l'objet JSON
        url = "http://api.openweathermap.org/data/2.5/forecast/daily?lat={lat:.02f}&lon={lon:.02f}&cnt={days}&mode=json&units=metric&lang=fr&APPID={apikey}"
        url = url.format(lat=location.latitude, lon=location.longitude, days=days, apikey=settings.OPENWEATHERMAP_API_KEY)
        resource = requests.get(url)
        if resource.status_code in (200, 304):
            value = resource.json()
            for item in value['list']:
                item['dt'] = datetime.datetime.utcfromtimestamp(item['dt'])
            # Mettre le résultat en cache pendant 12 heures
            cache.set(cache_key, value, 43200)
            return value
        elif resource.status_code == 401:
            raise ImproperlyConfigured(resource.text)
    return None
