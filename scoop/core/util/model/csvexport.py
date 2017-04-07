# coding: utf-8
import gzip
import os
from datetime import date, datetime

import unicodecsv as csv


def csv_dump(queryset, path, compress=False):
    """
    Exporter un queryset au format CSV

    :param compress: Enregistrer le dump dans un fichier gzip
    :type queryset: django.db.models.QuerySet
    :type path: str
    :type compress: bool
    """
    # TODO: Vérifier qu'on passe en Python3
    model = queryset.model
    if compress and not path.endswith(".gz"):
        path += ".gz"
    folder = os.path.dirname(path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    writer = csv.writer(gzip.open(path, 'wb') if compress else open(path, 'w+'), encoding='utf-8')
    # Écrire la liste des en-têtes
    headers = []
    for field in model._meta.fields:
        headers.append(field.name)
    writer.writerow(headers)
    # Écrire la liste des données du queryset
    for obj in queryset:
        row = []
        for field in headers:
            val = getattr(obj, field)
            if callable(val):
                val = val()
            if type(val) == str:
                val = val.encode("utf-8")
            if isinstance(val, (datetime, date)):
                val = val.strftime("%Y-%m-%d %H:%M:%S")
            row.append(val)
        writer.writerow(row)
    return True
