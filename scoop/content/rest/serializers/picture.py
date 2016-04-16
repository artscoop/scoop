# coding: utf-8
from rest_framework import serializers

from scoop.content.models.picture import Picture


class PictureSerializer(serializers.ModelSerializer):
    """ Serializer for pictures """

    # Métadonnées
    class Meta:
        model = Picture
