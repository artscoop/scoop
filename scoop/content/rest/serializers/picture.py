# coding: utf-8
from __future__ import absolute_import

from rest_framework import serializers

from scoop.content.models.picture import Picture


class PictureSerializer(serializers.ModelSerializer):
    """ Serializer for pictures """

    class Meta:
        model = Picture
