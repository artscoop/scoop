# coding: utf-8
import hashlib
from abc import ABCMeta, abstractmethod
from os.path import basename, splitext

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.db import models
from django.db.models.fields.files import FileField
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.util.data.uuid import uuid_bits


class ACLModel(models.Model):
    """
    Modèle dont le contenu fichier est protégé d'accès par des règles

    Le modèle non abstrait héritant de cette classe doit posséder un champ
    dérivé de FileField et un seul de préférence, et dont la propriété
    upload_to est définie à ACLModel.get_acl_upload_path
    """

    __metaclass__ = ABCMeta

    # Constantes
    ACL_MODES = [(0, pgettext_lazy('acl', "Public")), (1, pgettext_lazy('acl', "Registered")),
                 (2, pgettext_lazy('acl', "Private")), (3, pgettext_lazy('acl', "Friends")),
                 (5, pgettext_lazy('acl', "Custom"))]
    PUBLIC, REGISTERED, PRIVATE, FRIENDS, CUSTOM = 0, 1, 2, 3, 5
    ACL_PATHS = {0: 'public', 1: 'auth', 3: 'friends', 5: 'custom', 2: 'hidden'}
    ACL_PATHS_START = ('public', 'auth', 'friends', 'custom', 'hidden')
    DEFAULT_ACL_FOLDER = '{Y}/{M}'

    # Champs
    acl_mode = models.PositiveSmallIntegerField(default=PUBLIC, choices=ACL_MODES, verbose_name=_("Mode"))
    acl_custom = models.ForeignKey('content.customacl', null=True, verbose_name=_("ACL configuration"))

    # Getter
    def get_acl_directory(self):
        """
        Renvoyer le nom de répertoire d'ACL pour l'objet

        Les spreads permettent de disséminer des fichiers dans des sous-dossiers, afin
        que les cas de figure suivants ne se présentent jamais :
        - 64 000+ fichiers dans un seul répertoire (limite ext4)
        - 1 024+ fichiers dans un seul répertoire (lenteur Nautilus)
        Les spreads doivent être générés cryptographiquement :
        Si la méthode de génération de spread pour un fichier est connue et facile à prédire,
        alors on peut faire en sorte d'uploader des milliers de fichiers qui iront
        uniquement dans ce spread. Cela est potentiellement une attaque.
        Lorsque le spread est généré cryptographiquement, on ne peut pas utiliser cette
        attaque pour encombrer un répertoire (potentiel déni de service)
        """
        if self.acl_mode == self.REGISTERED:
            return self.ACL_PATHS[self.REGISTERED]
        elif self.acl_mode == self.PRIVATE:
            owner = self.get_acl_owner()
            return "{acl}/{spread}/{owner}".format(acl=self.ACL_PATHS[self.PRIVATE], owner=owner, spread=self._get_hash_path(owner))
        elif self.acl_mode == self.FRIENDS:
            owner = self.get_acl_owner()
            return "{acl}/{spread}/{owner}".format(acl=self.ACL_PATHS[self.FRIENDS], owner=owner, spread=self._get_hash_path(owner))
        elif self.acl_mode == self.CUSTOM and self.acl_custom:
            return self.acl_custom.get_acl_directory()
        else:
            return self.ACL_PATHS[self.PUBLIC]

    def get_acl_upload_path(self, filename, update=False):
        """
        Renvoyer le chemin d'upload du fichier

        :param self: instance d'objet. Hérite de préférence de DatetimeModel
        :param filename: nom du fichier uploadé. Peut être None, pour conserver le nom actuel
        :param update: indique que le fichier existait déjà et est resauvegardé
        """
        filename = filename.lower() if filename else self.get_filename() if self else uuid_bits(64)
        filename = filename.split('?')[0].split('#')[0] or uuid_bits(64)
        folder = getattr(settings, 'CONTENT_ACL_FOLDER', ACLModel.DEFAULT_ACL_FOLDER)
        # Créer les dictionnaires de données de noms de fichiers
        f = (self.get_datetime() if self else timezone.now()).strftime
        # Remplir le dictionnaire avec les informations de répertoire
        data = self.get_acl_upload_info()  # author
        data.update({'name': splitext(basename(filename))[0], 'ext': splitext(basename(filename))[1], 'type': self._meta.model_name,
                     'acl': self.get_acl_directory(), 'Y': f("%Y"), 'M': f("%m"), 'W': f("%W"), 'd': f("%d"), 'h': f("%H"), 'm': f("%M"), 's': f("%S")})
        # Renvoyer le répertoire ou le chemin complet du fichier (documenter)
        return "".join(["test/" if settings.TEST else "", "{acl}/{type}/", folder, "/{author}/{name}{ext}" if not update else ""]).format(**data)

    def get_acl_upload_info(self):
        """
        Renvoyer un dictionnaire d'informations sur l'objet, pour l'upload

        :returns: un dictionnaire avec au moins les clés author
        :rtype: dict
        """
        author = getattr(self, 'author', getattr(self, 'user', None))
        data = {'author': slugify(getattr(author, 'username', '__no_author'))}
        return data

    # Abstrait
    def get_acl_owner(self):
        """
        Renvoyer le nom d'utilisateur du propriétaire par défaut de l'objet

        :rtype: str
        """
        attributes = ('user', 'author', 'owner')
        for attribute in attributes:
            if hasattr(self, attribute):
                return getattr(self, attribute).username
        raise NotImplemented("The model does not have a user, author or owner. You must define get_acl_owner")

    @staticmethod
    def _get_hash_path(name):
        """
        Couper un nom en hash de répertoires

        ex. 'jean-michel' devient 'ac/2f/1d'
        Le chemin est calculé à partir des 24 premiers bits du hachage SHA-256
        Le hachage en sous-répertoires a plusieurs utilités :
        - il vaut mieux généralement avoir des répertoires pas trop peuplés, car en général il est plus difficile
          et plus long de lister le contenu d'un répertoire lorsqu'il y a beaucoup d'entrées. C'est valable
          dans une interface graphique du type Nautilus, mais c'est aussi valable en ligne de commande.
          Si par exemple nous avons 100 000 utilisateurs, et que l'on n'utilise pas de hash,
          on se retrouve alors avec un répertoire /friends, contenant 100 000 répertoires.
          Avec un hash, les sous-répertoires sont distribués sur une arborescence avec maximum 256 entrées par
          niveau et 3 niveaux (en tout cas dans le cas actuel, ça pourrait aller jusqu'à 32 niveaux théoriquement)
          Les sous répertoires sont de la forme 0a/19/3f/cd etc...
        - il vaut mieux utiliser des hashs que les premières lettres des noms d'utilisateur. Si tout le monde
          s'appelle r'^johnny\d+', on risque une concentration élevée d'entrées dans /jo/hn/ny. Avec un hash,
          on suppose généralement que 'johnny1' se trouve complètement ailleurs que 'johnny2'
        - un hachage solide permet d'empêcher un utilisateur d'utiliser les collisions et provoquer un
          dépassement du nombre d'entrées autorisées dans un répertoire (32000/64000 pour ext3/ext4)
        :returns: un sous-chemin de 3 répertoires, 6 caractères hexa.
        """
        digest = hashlib.sha256(name.encode('utf-8')).digest()
        for _hi in range(79):
            digest = hashlib.sha256(digest).digest()
        digest = digest.hex()
        parts = [digest[idx:idx + 2] for idx in range(0, 6, 2)]
        return '/'.join(parts)

    def _is_file_path_obsolete(self):
        """
        Renvoie si une mise à jour du chemin de fichier aura un quelconque effet

        En d'autres termes, est-ce que les paramètres de chemin de sauvegarde
        (via get_acl_upload_path) ont été modifiés après la création de ce fichier ?
        (ce qui signifie que ce fichier n'est pas stocké dans un répertoire
        conforme aux règles actuelles de stockage)
        """
        new_path = self.get_acl_upload_path(None)
        old_path = self.get_file_attribute().name
        return new_path != old_path

    # Action
    def update_file_path(self, force_name=None):
        """
        Déplacer le fichier vers son chemin par défaut

        :param force_name: nouveau nom de fichier, None si le nom doit rester inchangé
        :type force_name: str | NoneType
        :returns: True si l'opération est un succès, False sinon
        """
        if self.exists():
            # Supprimer les fichiers liés si besoin, etc.
            self.prepare_file_path_update()
            # Changer la position du fichier
            file_attribute = self.get_file_attribute()
            new_path = self.get_acl_upload_path(force_name, update=bool(force_name))
            old_path = file_attribute.name
            # Puis recréer le fichier dans le nouveau chemin. Ne rien faire si le nom est inchangé, car voir commentaire suivant
            if new_path != old_path:  # https://docs.djangoproject.com/en/1.10/_modules/django/core/files/storage/#Storage.get_available_name
                with File(file_attribute) as original:
                    file_attribute.open()
                    file_attribute.save(new_path, original)
                    file_attribute.close()
                    self.save(force_update=True, update_fields=[self._get_file_attribute_name()])
                default_storage.delete(old_path)
                return True
        else:
            # Supprimer l'entrée si le fichier cible n'existe pas
            self.delete()
        return False

    # Obligatoire
    def prepare_file_path_update(self):
        """
        Préparer les dépendances au fichier avant de le déplacer

        ex. Pour Picture, on supprime au préalable les miniatures
        """
        pass

    @abstractmethod
    def get_filename(self, extension=True):
        """
        Renvoyer le nom de fichier seul, avec ou sans l'extension

        ex. /a/b/c/file.txt devient file ou file.txt
        :param extension: renvoyer le nom de fichier avec extension
        """
        raise NotImplemented("Your model must implement get_filename.")

    def _get_file_attribute_name(self):
        """
        Renvoie le nom de l'attribut fichier pour le modèle

        :rtype: str
        :returns: ex. 'image' ou 'file'
        """
        # Par défaut, parcourir les champs à la recherche d'un FileField
        return (field.name for field in self._meta.get_fields() if isinstance(field, FileField))[0]

    def get_file_attribute(self):
        """ Renvoie directement le champ fichier de l'instance """
        return getattr(self, self._get_file_attribute_name())

    # Overrides
    def save(self, *args, **kwargs):
        """ Sauvegarder l'objet """
        super().save(*args, **kwargs)
        if getattr(settings, 'CONTENT_ACL_AUTO_UPDATE_PATHS', False):
            if self._is_file_path_obsolete():
                self.update_file_path()

    # Métadonnées
    class Meta:
        permissions = [('define_acl_%(class)s', "Can define ACL configurations for %(class)s")]
        abstract = True
