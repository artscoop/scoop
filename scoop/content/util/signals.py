# coding: utf-8
""" Signaux de l'application contenu """
from django.dispatch import Signal


content_created = Signal(['instance'])
content_expired = Signal(['instance'])
content_pre_save = Signal(['instance'])
content_pre_lock = Signal(['instance', 'value', 'author'])  # renvoyer false si lock interdit
content_format_html = Signal(['instance'])  # Modifier le HTML une fois généré
# Commentaire posté
comment_posted = Signal(['target'])
comment_spam = Signal(['spam'])
# Commentaire accepté par le demandeur
comment_accepted = Signal([])
# Contenu mis à jour ou avec un nouveau commentaire
content_updated = Signal(['instance'])
