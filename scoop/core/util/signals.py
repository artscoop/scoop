# coding: utf-8
from django.dispatch import Signal

# Création d'un nouvel enregistrement
record = Signal(['actor', 'action', 'target', 'content'])
# Un ping de serveur XMLRPC de blog a échoué
ping_failed = Signal(['engine', 'feed'])
# Check si un élément peut être indexé
check_indexable = Signal(['instance'])  # Renvoie True si indexable, sinon None
