# coding: utf-8
from __future__ import absolute_import

from django.dispatch import Signal

# IP bloquée pour un utilisateur
user_has_ip_blocked = Signal(['ip', 'harm'])
# IP définie offensive
ip_harmful = Signal()
ip_blocked = Signal(['harm'])
# Flag créé
flag_created = Signal(providing_args=['flag'])
flag_closed = Signal(providing_args=['flag'])
# Flag à résoudre. iteration correspond au nombre de flags déjà résolus
flag_resolve = Signal(providing_args=['iteration'])
# Blocklist créé
blocklist_added = Signal(['user', 'name'])
