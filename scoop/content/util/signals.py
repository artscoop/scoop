# coding: utf-8
""" Signaux de l'application contenu """
from django.dispatch import Signal

content_created = Signal(providing_args=['instance'])
content_expired = Signal(providing_args=['instance'])
content_pre_save = Signal(providing_args=['instance'])
content_pre_lock = Signal(['instance', 'value', 'author'])  # renvoyer false si lock interdit
# Commentaire posté
comment_posted = Signal(['target'])
comment_spam = Signal(['spam'])
# Commentaire accepté par le demandeur
comment_accepted = Signal(providing_args=[])
