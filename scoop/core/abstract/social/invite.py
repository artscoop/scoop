# coding: utf-8
from django.db import models


class InviteTargetModel(models.Model):
    """ Cet objet est une entité à laquelle on peut inviter des utilisateurs """

    # Getter
    def is_invite_content(self):
        """ Renvoyer que l'objet est un contenu accessible aux invitations """
        return True

    # Métadonnées
    class Meta:
        abstract = True
