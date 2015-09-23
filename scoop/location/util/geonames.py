# coding: utf-8
from __future__ import absolute_import

import csv
import datetime
import gc
import os
import re
import sys
import tempfile
import traceback
from csv import excel_tab
from os.path import join
from traceback import print_exc

import pytz
from celery import task
from django.conf import settings
from django.contrib.gis.geos.point import Point
from django.db import transaction
from django.db.models import Q
from django.db.utils import DatabaseError
from django.utils import timezone
from unidecode import unidecode

from scoop.core.util.stream.directory import Paths
from scoop.core.util.stream.fileutil import auto_open_file, open_zip_file
from scoop.core.util.stream.urlutil import download_url_resource
from scoop.location.models import City, CityName, Country, CountryName, Currency, Timezone

# Codes Feature : http://www.geonames.org/export/codes.html
# Fichiers Villes : http://download.geonames.org/export/dump/
# Total des noms alternatifs : http://www.geonames.org/statistics/
csv.field_size_limit(16777216)
ALTERNATES_COUNT = 10223616  # 2015/08/09


class ExcelNoQuote(excel_tab):
    """ Dialecte CSV, les double quotes font partie du contenu """
    quoting = csv.QUOTE_NONE


def load_geoname_table_raw(path, filename):
    """ Renvoyer un reader CSV vers une table de pays Geonames """
    handle = open_zip_file(path, filename)
    # columns = ['id', 'name', 'ascii', 'alternate', 'latitude', 'longitude', 'f1', 'feature', 'country', 'c1', 'zone1', 'zone2', 'zone3', 'zone4', 'population', 'elevation', 'gtopo', 'timezone', 'updated']
    return csv.reader(handle, dialect='excel-tab')


def load_currency_table(path, filename):
    """ Renvoyer un reader CSV sur la liste de pays avec devises """
    handle = auto_open_file(path, filename)
    columns = ['sortorder', 'commonname', 'formalname', 'type', 'subtype', 'sovereignty', 'capital', 'iso4217currencycode', 'iso4217currencyname', 'ituttelephonecCode', 'iso316612lettercode',
               'iso316613lettercode', 'iso31661number', 'ianacountrycodetld']
    return csv.DictReader(handle, columns, dialect='excel'), handle


def load_geoname_alternate_table_raw(path, filename):
    """ Renvoyer un reader CSV sur la table de noms alternatifs Geonames """
    handle = open_zip_file(path, filename)
    # columns = ['altid','geoid','lang','name','preferred','short','slang','historic']
    return csv.reader(handle, dialect=ExcelNoQuote)


def load_geoname_country_table(path, filename):
    """ Renvoyer un reader CSV sur une table de pays """
    handle = auto_open_file(path, filename)
    columns = ['code2', 'code3', 'iso', 'fips', 'name', 'capital', 'area', 'population', 'continent', 'tld', 'currency', 'currencyname', 'phone', 'postalformat', 'postalregex', 'languages',
               'geoid', 'neighbours', 'eqfips']
    return csv.DictReader(handle, columns, dialect='excel-tab')


def output_progress(s, idx, rows, every, items):
    """ Afficher la progression d'une opération """
    if idx % every == 0 or idx == rows:
        percent = round(100.0 * idx / rows, 1)
        items.update({'pc': percent, 'idx': idx, 'rows': rows})
        sys.stdout.write((s + " " * 20 + "\r").format(**items))
        sys.stdout.flush()


@transaction.atomic
def populate_countries(rename=True):
    """ Peupler la base des pays """
    try:
        filename = os.path.join(settings.STATIC_ROOT, "assets", "geonames", "country")
        reader = load_geoname_country_table(filename, 'country')
        for row in reader:
            if not row['code2'].startswith("#") and row['geoid']:
                phone_extract = re.findall(r"^([\d\-\+]+)", row['phone'])
                phone_prefix = phone_extract[0] if phone_extract else ""
                kwargs = {'id': row['geoid'], 'name': row['name'], 'code2': row['code2'], 'code3': row['code3']}
                country, _ = Country.objects.update_or_create(**kwargs)
                country.update(**{'capital': row['capital'], 'population': row['population'] or 0, 'area': row['area'] or 0, 'continent': row['continent'], 'phone': phone_prefix})
                country.set_data('neighbours', row['neighbours'])
                country.save()
        if rename is True:
            rename_countries()
        return True
    except ValueError:
        return False


@transaction.atomic
def rename_countries(output_every=262144):
    """ Peupler les noms alternatifs des pays """
    # [0: alternate_id, 1: geonames_id, 2: lang, 3: name, 4: preferred, 5: short, 6: slang, 7: historic]
    filename = None
    try:
        default_path = join(Paths.get_root_dir('files', 'geonames'), 'alternateNames.zip')
        filename = default_path if os.path.exists(default_path) else download_url_resource('http://download.geonames.org/export/dump/alternateNames.zip')
        reader = load_geoname_alternate_table_raw(filename, 'alternateNames')
        LANGUAGES = frozenset([item[0] for item in settings.LANGUAGES])
        COUNTRY_IDS = frozenset(set(Country.objects.all().values_list('id', flat=True)))
        # Récupérer la taille de la table en lignes
        rows, affected = ALTERNATES_COUNT, 0
        # Traiter immédiatement le ficiher
        CountryName.objects.all().delete()
        for idx, row in enumerate(reader, start=1):
            if row[2] and row[1] and not (row[6] or row[7]) and row[2] in LANGUAGES:
                geonames_id, alternate_id = int(row[1]), int(row[0])
                if geonames_id in COUNTRY_IDS:
                    CountryName.objects.create(id=alternate_id, country_id=geonames_id, language=row[2], name=row[3], preferred=row[4] == '1', short=row[5] == '1')
                    affected += 1
            if idx % output_every == 0 or idx == rows:
                output_progress("Renaming: {pc:>5.1f}% ({idx:>10}/{rows:>10}, {affected:>10} updated)", idx, rows, output_every, {'affected': affected})
        sys.stdout.write("\n")
        reader.close()
        gc.collect()
        return True
    except Exception:
        return False
    finally:
        if filename:
            os.unlink(filename)


@transaction.atomic
def populate_cities(country, output_every=8192):
    """
    Peupler la base de données avec des subdivisions administratives
    Ces subdivisions sont : ^ADM\d$ et ^PPL.{0,2}$
    ADM : Zone administrative : région, département, etc. jusqu'à commune ( :/ )
    PPL : Ville, lieu habité nommé (contient beaucoup de spam)
    """
    # [0id, 1name, 2ascii, 3alternate, 4latitude, 5longitude, 6f1, 7feature, 8country, 9c1, 10zone1, 11zone2, 12zone3, 13zone4, 14population, 15elevation, 16gtopo, 17timezone, 18updated]
    if not settings.DEBUG:
        try:
            used_features, unused_features = {'ADM', 'PPL'}, {'PCLH', 'PCLI', 'PCLIX', 'PCLS', 'ADM1H', 'ADM2H', 'ADM3H', 'ADM4H', 'PPLCH', 'PPLF', 'PPLH', 'PPLQ', 'PPLR', 'PPLW'}
            country_name = country.get_name()
            # Remplir un dictionnaire avec la liste des lignes
            default_path = join(Paths.get_root_dir('files', 'geonames'), '{country}.zip'.format(country=country.code2.upper()))
            filename = default_path if os.path.exists(default_path) else download_url_resource('http://download.geonames.org/export/dump/{country}.zip'.format(country=country.code2.upper()),
                                                                                               '{path}/geonames-country-{country}.zip'.format(path=tempfile.gettempdir(),
                                                                                                                                              country=country.code2.upper()))
            reader, table = load_geoname_table_raw(filename, unidecode(country.code2)), {}
            for row in reader:
                if len(row) > 17 and row[7][:3] in used_features and row[7] not in unused_features:
                    table[int(row[0])] = row
            # Récupérer la taille de la table en lignes
            timezones = Timezone.get_dict()
            rows, updated_count = len(table), 0
            # Mettre à jour la table des villes du pays
            if City.objects.filter(country=country).exists():
                db_ids = frozenset(set(City.objects.filter(country=country).values_list('id', flat=True)))
                # Effacer de la base les éléments qui ne sont plus dans la nouvelle table (ex. PPL devenu MNT)
                table_ids = frozenset(set(table.keys()))
                removed_ids = db_ids.difference(table_ids)
                City.objects.filter(id__in=removed_ids).delete()
                sys.stdout.write("{} items were removed from the database.\n".format(len(removed_ids)))
                sys.stdout.flush()
                # Traiter le reste
                for idx, row in enumerate(table.values(), start=1):
                    geoid, updateable = int(row[0]), datetime.datetime.strptime(row[18], '%Y-%m-%d').replace(tzinfo=pytz.utc) >= country.updated
                    latitude, longitude = float(row[4]), float(row[5])
                    city = City(id=geoid, level=0, country=country, timezone=timezones[row[17]], name=row[1], ascii=row[2].lower(), a1=row[10], a2=row[11], a3=row[12], a4=row[13], type=row[7],
                                feature=row[6], city=(row[6] == 'P'), population=int(row[14]), position=Point(longitude, latitude))
                    if updateable or geoid not in db_ids:
                        city.save()
                        updated_count += int(updateable)
                    if idx % output_every == 0 or idx == rows - 1:
                        output_progress("Updating {country:>15}: {pc:>5.1f}% ({idx:>10}/{rows:>10}, {updated:>10} updated)", idx, rows, output_every,
                                        {'country': country_name, 'updated': updated_count})
            # Peupler la liste des villes si aucune n'existe pour le pays
            else:
                bulk = []
                for idx, row in enumerate(table.values(), start=1):
                    latitude, longitude = float(row[4]), float(row[5])
                    city = City(id=int(row[0]), level=0, country=country, timezone=timezones[row[17]], name=row[1], ascii=row[2], a1=row[10], a2=row[11], a3=row[12], a4=row[13], type=row[7],
                                feature=row[6], city=row[6] == 'P', population=int(row[14]), position=Point(longitude, latitude))
                    bulk.append(city)
                    if idx % output_every == 0 or idx == rows - 1:
                        output_progress("Filling {country:>15}: {pc:>5.1f}% ({idx:>10}/{rows:>10})", idx, rows, output_every, {'country': country_name})
                City.objects.bulk_create(bulk)
            # Les portions de ville sont ensuite marquées comme non villes
            gc.collect()
            City.objects.filter(type='PPLX').update(city=False)
            country.update(updated=timezone.now(), public=True, save=True)
            return True
        except Exception as e:
            traceback.print_exc(e)
            return False
    else:
        print("Operation not launched, disable DEBUG first.")


@task
@transaction.atomic
def rename_cities(output_every=262144):
    """ Peupler les noms alternatifs des villes """
    # [0:altid,1:geoid,2:lang,3:name,4:preferred,5:short,6:slang,7:historic]
    if not settings.DEBUG:
        try:
            default_path = join(Paths.get_root_dir('files', 'geonames'), 'alternateNames.zip')
            filename = default_path if os.path.exists(default_path) else download_url_resource('http://download.geonames.org/export/dump/alternateNames.zip')
            reader = load_geoname_alternate_table_raw(filename, 'alternateNames')
            languages = frozenset([language[0] for language in settings.LANGUAGES] + ['post', ''])
            affected, existing = 0, frozenset(set(City.objects.values_list('id', flat=True)))
            citynames = []
            # Traiter immédiatement le ficiher
            CityName.objects.all().delete()
            for idx, row in enumerate(reader, start=1):
                if (row[2] in languages and row[1]) and not (row[6] or row[7]):
                    if int(row[1]) in existing:
                        ascii = unidecode(row[3].decode('utf-8') if type(row[3]) != str else row[3]).lower()
                        cityname = CityName(id=int(row[0]), city_id=int(row[1]), language=row[2], name=row[3], ascii=ascii, preferred=(row[4] == '1'), short=(row[5] == '1'))
                        citynames.append(cityname)
                        affected += 1
                if idx % output_every == 0 or idx == ALTERNATES_COUNT:
                    output_progress("Renaming: {pc:>5.1f}% ({idx:>10}/{rows:>10}, {affected:>10} updated)", idx, ALTERNATES_COUNT, output_every, {'affected': affected})
            CityName.objects.bulk_create(citynames, batch_size=32768)
            return True
        except Exception as e:
            print_exc(e)
            return False
        finally:
            gc.collect()
    return False


@task
def populate_currency(country):
    """ Peupler les devises """
    filename = os.path.join(settings.STATIC_ROOT, "assets", "geonames", "country")
    reader, _ = load_currency_table(filename, 'countrylist')
    if country.currency is None:
        for row in reader:
            if country.code3.lower() == row['iso316613lettercode'].lower():
                try:
                    currency = Currency.objects.get(name=row['iso4217currencyname'], short_name=row['iso4217currencycode'])
                except Currency.DoesNotExist:
                    currency = Currency.objects.create(name=row['iso4217currencyname'], short_name=row['iso4217currencycode'])
                country.currency = currency
                country.save()
                break


@task
@transaction.atomic
def reparent_cities(country, clear=False, output_every=256):
    """ Réorganiser la hiérarchie des villes d'un pays """
    if not settings.DEBUG:
        # Récupérer les éléments de type A (ex. ADM1)
        if clear:
            City.objects.filter(country=country).update(parent=None)
        parents = City.objects.filter(Q(feature='A') | Q(type__in=['PPLA', 'PPLA2', 'PPLA3', 'PPLA4']), country=country).order_by('type').distinct()
        rows = parents.count()
        country_name = country.get_name()
        # Parcourir ces éléments et mettre à jour les enfants directs
        for idx, parent in enumerate(parents, start=1):
            level, acodes = 1, [parent.a1, parent.a2, parent.a3, parent.a4]
            # Trouver le niveau administratif actuel de l'élément
            for i, acode in enumerate(acodes, start=1):
                level = i if acode != "" else level
            # Update les P et ADMD enfants
            criteria = {'a{0}'.format(i): v for i, v in enumerate(acodes, start=1)}
            criteria.update({'country': country, 'parent': None})
            type_filter = (Q(feature='P') | Q(type="ADMD")) if parent.type != 'ADMD' else Q(feature='P')
            City.objects.filter(type_filter, **criteria).exclude(id=parent.id).update(parent_id=parent.id, level=level)
            # Update les A enfants
            if level < 4 and parent.feature == "A" and parent.type not in {'ADMD'}:
                criteria.update({'feature': 'A'})
                del criteria['a{0}'.format(level + 1)]
                exclusion = {'a{0}'.format(level + 1): ''}
                City.objects.filter(**criteria).exclude(id=parent.id, **exclusion).update(parent_id=parent.id, level=level)
            # Sortie logging ou console
            if idx % output_every == 0 or idx == rows - 1:
                output_progress("Rebuilding {country}: {pc:>5.1f}% ({idx:>10}/{rows:>10})", idx, rows, output_every, {'country': country_name})
        # Calculer la latitude et longitude moyennes du pays
        all_cities = City.objects.filter(country=country, city=True).only('position')
        city_count = all_cities.count()
        average_latitude = sum([city.position.y for city in all_cities]) / city_count
        average_longitude = sum([city.position.x for city in all_cities]) / city_count
        country.position = Point(average_longitude, average_latitude)
        country.updated = timezone.now()
        country.save()
        gc.collect()
        return True
    return False
