# coding: utf-8
"""
Code original par Sunil Arora (15.02.2010)
Disponible à l'adresse http://sunilarora.org/parsing-signedrequest-parameter-in-python-bas

Lorsque vous vous inscrivez à l'aide de Facebook, le site fournit en retour les
informations d'inscription que l'utilisateur a fourni, à l'aide d'une requête POST
à l'adresse indiquée (dans les paramètres Facebook), et dont l'attribut signed_request
est une liste au format JSON crypté à l'aide de l'algorithme HMAC-SHA256. La clé de cryptage
est la clé secrète de l'application Facebook.
"""

import base64
import hashlib
import hmac

import simplejson as json


def parse_signed_request(signed_request, secret):
    """ Parcourir une requête signée venant de Facebook """
    def base64_url_decode(encoded):
        padding_factor = (4 - len(encoded) % 4) % 4
        encoded += "=" * padding_factor
        return base64.b64decode(unicode(encoded).translate(dict(zip(map(ord, u'-_'), u'+/'))))

    # La requête est séparée en 2 : signature et payload (données)
    l = signed_request.split('.', 2)
    decoded_signature = base64_url_decode(l[0])
    data = json.loads(base64_url_decode(l[1]))
    # Vérifier que l'algorithme utilisé est HMAC-SHA256
    if data.get('algorithm').upper() != 'HMAC-SHA256':
        return None
    # Si l'algorithme est SHA256, réencoder pour voir si on retrouve bien ce qu'on a reçu
    else:
        expected_sig = hmac.new(secret, msg=data, digestmod=hashlib.sha256).digest()
    # Si cela ne correspond pas, il y a un problème, avorter l'opération
    if decoded_signature != expected_sig:
        return None
    else:
        return data
