# coding: utf-8
import gc
import time

from celery import task
from django.utils.translation import ugettext as _
from scoop.location.util.geonames import populate_cities, populate_currency, rename_cities, reparent_cities


@task
def geonames_fill(countries):
    """ Importer toutes les informations d'un ou plusieurs pays """
    renaming_allowed = False
    for country in countries:
        print("Starting population for {}".format(country.name))
        gc.disable()
        start_time = time.time()
        if populate_cities(country) is True:
            renaming_allowed = True
            reparent_cities(country)
            populate_currency(country)
            print("population was successfully run in {time:.02f} seconds.".format(time=time.time() - start_time))
        else:
            print(_("population has failed. please investigate."))
        gc.enable()
    if renaming_allowed:
        gc.disable()
        start_time = time.time()
        rename_cities()
        print("\nrenaming was successfully done in {time:.02f} seconds.".format(time=time.time() - start_time))
        gc.enable()
    return True
