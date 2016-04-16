# coding: utf-8
from rest_framework import serializers

from scoop.content.models.content import Content


class ContentSerializer(serializers.ModelSerializer):
    """ Serializer for content """

    # Métadonnées
    class Meta:
        model = Content
