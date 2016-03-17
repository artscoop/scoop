# coding: utf-8
""" Signaux de l'application User """
from django.dispatch import Signal

# Inscription
registration_completed = Signal(providing_args=['request', 'user'])
# Champs d'inscription : lever forms.ValidationError si invalide
credentials_form_check_email = Signal(['email'])
credentials_form_check_name = Signal(['name'])
credentials_form_check_username = Signal(['username'])
# Statut utilisateur
user_activated = Signal(['user', 'request', 'failed'])  # Utilisateur activé/réactivé
user_deactivated = Signal(['user', 'request'])  # Utilisateur désactivvé
user_demoted = Signal(['user'])  # Utilisateur déchû du rôle staff
user_edited = Signal(['user'])  # Utilisateur modifié
# Statut de profil
profile_banned = Signal(['user'])  # Profil banni
profile_viewed = Signal(['visitor', 'user'])  # Profil affiché
online_status_updated = Signal(['online'])  # Le statut de connexion a changé
profile_picture_changed = Signal()  # L'image principale du profil a changé
# IP utilisateur
userip_created = Signal()  # Nouvelle IP pour un utilisateur
# Utilisateurs anonymes
external_visit = Signal(['referrer', 'path', 'request'])  # Une page a été vue via un referrer

# État d'abandon des profils
# vérifier qu'un profil est laissé à l'abandon
check_stale = Signal(['user', 'profile'])  # le profil est abandonné si tous les listeners renvoient True
# Vérifier qu'un profil n'a jamais servi.
check_unused = Signal(['user', 'profile'])  # le profil est inutilisé si tous les listeners renvoient True

# Manipuler le queryset de recherche par défaut de profils pour un utilisateur
profile_default_search_criteria = Signal(['profile'])  # Renvoyer les critères de filtre de queryset par défaut
