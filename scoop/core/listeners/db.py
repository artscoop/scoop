# coding: utf-8
from django.db.backends.signals import connection_created
from django.dispatch.dispatcher import receiver

__all__ = ['activate_pragmas']


@receiver(connection_created)
def activate_pragmas(sender, connection, **kwargs):
    """ Activer des options des performance pour SQLite """
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys = ON;')
        cursor.execute('PRAGMA synchronous = OFF;')
        cursor.execute('PRAGMA temp_store = MEMORY;')
