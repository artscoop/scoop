# coding: utf-8
import datetime

import requests

from django.core.cache import cache
from django.template.defaultfilters import slugify
from scoop.core.abstract.location.coordinates import CoordinatesModel


def get_open_weather(location, days=6):
    """ Renvoyer les données de météo OpenWeatherMap 2.0 """
    if isinstance(location, CoordinatesModel) and isinstance(days, (int, float)):
        # Récupérer la météo en cache si possible
        cache_key = "location.weather.{type}.{id}.{days}".format(type=slugify(location._meta.object_name), id=location.pk, days=days)
        cached = cache.get(cache_key, None)
        if cached is not None:
            return cached
        # Appeler l'API de Open Weather Map et récupérer l'objet JSON
        url = "http://api.openweathermap.org/data/2.5/forecast/daily?lat={lat}&lon={lon}&cnt={days}&mode=json&units=metric&lang=fr".format(lat=location.latitude, lon=location.longitude,
                                                                                                                                           days=days)
        resource = requests.get(url)
        value = resource.json()
        for item in value['list']:
            item['dt'] = datetime.datetime.utcfromtimestamp(item['dt'])
        # Mettre le résultat en cache pendant 12 heures
        cache.set(cache_key, value, 43200)
        return value
    return None
