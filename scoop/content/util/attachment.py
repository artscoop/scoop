# coding: utf-8
import os

from django.conf import settings
from django.utils import timezone
from unidecode import unidecode


def get_attachment_upload_path(attachment, name, update=False):
    """
    Définir le chemin et le nom de fichier par défaut des uploads de pièces jointes.

    :param attachment: instance de modèle de pièce jointe
    :param name: nom du fichier uploadé
    :param update: mettre à jour le chemin mais conserver le nom de fichier
    """
    name = (unidecode(name).lower())
    name = name.split('?')[0].split('#')[0]
    # Créer un dictionnaire de données pour le nom de répertoire
    now = timezone.now()
    now_fmt = now.strftime
    author = ("{}".format(attachment.author)) if attachment.author is not None else "__"
    dir_info = {'year': now_fmt("%Y"), 'month': now_fmt("%m"), 'day': now_fmt("%d")}
    prefix_info = {'hour': now_fmt("%H"), 'minute': now_fmt("%M"), 'second': now_fmt("%M"), 'author': author}
    name_info = {'name': os.path.splitext(name)[0], 'ext': os.path.splitext(name)[1]}
    data = dict(dir_info.items() + name_info.items() + prefix_info.items())
    # Renvoyer le répertoire ou le chemin complet du fichier
    if update is True:
        path = "file/join/{year}/{month}/{day}".format(**data)  # déplacer sans modifier le nom
    else:
        path = "file/join/{year}/{month}/{day}/{author}-{hour}{minute}{second}-{name}{ext}".format(**data)  # définir et préfixer le nom
    if settings.TEST:
        path = "test/{}".format(path)
    return path
