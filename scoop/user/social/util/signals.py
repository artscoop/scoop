# coding: utf-8
""" Signaux de l'application Social """
from django.dispatch import Signal

# Demande d'amitié à lancer
friend_pending_new = Signal(['recipient'])
friend_accepted = Signal(['recipient'])
friend_denied = Signal(['recipient'])
# Invitation à un contenu acceptée
invite_accepted = Signal(providing_args=['instance'])
invite_denied = Signal(providing_args=['instance'])
# Événement
event_date_changed = Signal(['instance'])
