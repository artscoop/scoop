# coding: utf-8
from celery import task
from scoop.location.util.weather import get_open_weather


@task(expires=30, rate_limit='10/m')
def weather_prefetch(city):
    """ Précharger les informations météo pour une ville """
    get_open_weather(city)
