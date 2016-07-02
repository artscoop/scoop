# coding: utf-8
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models


class SubscribableModel(models.Model):
    """ Objet auquel on peut s'abonner """

    # Champs
    subscriptions = GenericRelation('content.subscription')

    # Getter
    def get_subscriptions(self):
        """ Renvoyer les abonnements à ce contenu """
        return self.subscriptions.all()

    # Métadonnées
    class Meta:
        abstract = True
