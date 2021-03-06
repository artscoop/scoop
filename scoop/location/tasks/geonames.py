# coding: utf-8
import time

from celery import task
from django.utils.translation import ugettext as _
from scoop.location.util.geonames import populate_cities, populate_currency, rename_cities, reparent_cities


@task(expires=60)
def geonames_fill(countries, rename=True):
    """ Importer toutes les informations d'un ou plusieurs pays """
    renaming_allowed = False
    for country in countries:
        print("Starting population for {}".format(country.name))
        start_time = time.time()
        if populate_cities(country) is True:
            renaming_allowed = True
            reparent_cities(country)
            populate_currency(country)
            print("population was successfully run in {time:.02f} seconds.".format(time=time.time() - start_time))
        else:
            print(_("population has failed. please investigate."))
    if renaming_allowed and rename:
        start_time = time.time()
        rename_cities()
        print("\nrenaming was successfully done in {time:.02f} seconds.".format(time=time.time() - start_time))
    return True
