# coding: utf-8
from django.dispatch import Signal


# Fil de discussion sur le point d'être créé
thread_pre_create = Signal(['author', 'recipients', 'request', 'unique', 'force'])  # renvoie True ou un dict {'messages': list}
thread_created = Signal(['author', 'thread'])
thread_read = Signal(['user', 'thread'])
# Message envoyé
message_pre_send = Signal(['author', 'thread', 'request'])
message_sent = Signal(['author', 'message', 'request'])
message_set_spam = Signal(['message'])
message_check_spam = Signal(['message'])  # ne pas sauvegarder l'objet
# Événement provoquant l'envoi d'un mail
mailable_event = Signal(['mailtype', 'recipient', 'data'])
# negotiation de messagerie
negotiation_sent = Signal(['source', 'target'])
negotiation_accepted = Signal(['source', 'target'])
negotiation_denied = Signal(['source', 'target'])
