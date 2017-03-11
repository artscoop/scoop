# coding: utf-8
import uuid
import zlib

from django.utils.baseconv import base64


def uuid_bits(bits=64):
    """
    Renvoyer un UUID tronqué à n bits.

    :param bits: nombre de bits de l'UUID. Entre 16 et 1024
    :returns: une chaîne en base64 représentant une valeur 'uuid' sur n bits
    """
    output = []
    bits = min(1024, max(16, bits))
    while bits > 128:
        value = str(uuid.uuid4()).replace('-', '')
        value = int(value, 16)
        value = base64.encode(value)
        output.append(value)
        bits -= 128
    value = str(uuid.uuid4()).replace('-', '')
    value = int(value, 16) >> (128 - bits)
    value = base64.encode(value)
    output.append(value)
    return ''.join(output)


def int_shorten(value):
    """ Renvoyer la représentation Base64 d'un entier """
    result = base64.encode(value)
    return result


def string_hash32(value):
    """ Renvoyer un hash 32 bits d'une chaîne """
    result = zlib.adler32(value) & 0xffffffff
    return result
