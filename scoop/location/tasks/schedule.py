# coding: utf-8
from __future__ import absolute_import

from celery.schedules import crontab, timedelta
from celery.task import periodic_task
from django.utils.translation import ugettext_lazy as _

from scoop.location.models import City, Currency


@periodic_task(run_every=crontab(hour=0, minute=1))
def update_currency_balances():
    """ Mettre à jour les valeurs des devises """
    return Currency.objects.update_balances()


@periodic_task(run_every=timedelta(minutes=30))  # 20 minutes = 48 appels/jour
def auto_fetch_city_pictures():
    """ Ajouter progressivement des images aux villes de 15 000+ habitants """
    cities = City.objects.by_population(['FR'], 15000).filter(city=True, pictured=False).order_by('-population')
    fetch_count = 0
    if cities.exists():
        for city in cities[0:2]:  # 2 requêtes max par appel : 96 requêtes/jour
            if not city.has_pictures({}):  # aucun filtre sur les images modérées
                fetched = city.fetch_picture()
                fetch_count += fetched
                print(_("Successfully fetched {count} images for city {city}").format(count=fetched, city=city))
    return {'fetched': fetch_count}
