# coding: utf-8
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models


class SubscribableModel(models.Model):
    """ Objet auquel on peut s'abonner """

    # Champs
    subscriptions = GenericRelation('content.subscription')

    # Métadonnées
    class Meta:
        abstract = True
