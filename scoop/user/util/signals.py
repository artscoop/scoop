# coding: utf-8
""" Signaux de l'application User """
from __future__ import absolute_import

from django.dispatch import Signal

# Inscription
registration_completed = Signal(providing_args=['request', 'user'])
# Champs d'inscription : lever forms.ValidationError si invalide
credentials_form_check_email = Signal(['email'])
credentials_form_check_name = Signal(['name'])
credentials_form_check_username = Signal(['username'])
# Statut utilisateur
user_activated = Signal(['user', 'request', 'failed'])
user_deactivated = Signal(['user', 'request'])
user_demoted = Signal(['user'])
user_edited = Signal(['user'])
# Statut de profil
profile_banned = Signal(['user'])
profile_viewed = Signal(['visitor', 'user'])
online_status_updated = Signal(['online'])
profile_picture_changed = Signal()
# IP utilisateur
userip_created = Signal()
# Utilisateurs anonymes
external_visit = Signal(['referrer', 'path', 'request'])

# État d'abandon des profils
check_stale = Signal(['user', 'profile'])  # vérifier qu'un profil est laissé à l'abandon
check_unused = Signal(['user', 'profile'])  # Vérifier qu'un profil n'a jamais servi

# Manipuler le queryset de recherche par défaut de profils pour un utilisateur
profile_default_search_criteria = Signal()
