# coding: utf-8
import uuid
import zlib

from django.utils.baseconv import base64


def uuid_bits(bits=64):
    """
    Renvoyer un pseudo-UUID sur n bits, en base64
    
    Note: 6 bits = 1 caractère

    :param bits: nombre de bits de l'UUID. Entre 16 et 1024
    :returns: une chaîne en base64 représentant une valeur 'uuid' sur n bits
    """
    bits = min(1024, max(16, bits))
    val_shift = 1
    total = 0
    while bits > 128:
        value = str(uuid.uuid4()).replace('-', '')
        total += int(value, 16) * val_shift
        bits -= 128
        val_shift *= 2 ** 128
    value = str(uuid.uuid4()).replace('-', '')
    total += (int(value, 16) >> (128 - bits)) * val_shift
    output = base64.encode(total)
    return output


def int_shorten(value):
    """ Renvoyer la représentation Base64 d'un entier """
    result = base64.encode(value)
    return result


def string_hash32(value):
    """ Renvoyer un hash 32 bits d'une chaîne """
    result = zlib.adler32(value) & 0xffffffff
    return result
