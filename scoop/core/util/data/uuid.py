# coding: utf-8
from __future__ import absolute_import

import uuid
import zlib

from django.utils.baseconv import base64


def uuid_bits(bits=64):
    """ Renvoyer un UUID tronqué à n bits """
    value = str(uuid.uuid4()).replace('-', '')
    value = int(value, 16) >> (128 - bits)
    value = base64.encode(value)
    return value


def int_shorten(value):
    """ Renvoyer la représentation Base64 d'un entier """
    result = base64.encode(value)
    return result


def string_hash32(value):
    """ Renvoyer un hash 32 bits d'une chaîne """
    result = zlib.adler32(value) & 0xffffffff
    return result
