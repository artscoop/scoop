# coding: utf-8
from django.dispatch import Signal

# Vote effectué
poll_vote_cast = Signal()
# Sondage fermé / ouvert
poll_closed = Signal(['instance'])
poll_opened = Signal(['instance'])

# Fil de discussion
forum_pre_post = Signal(['author'])
