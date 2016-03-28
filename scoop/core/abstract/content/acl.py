# coding: utf-8
import hashlib
from abc import ABCMeta, abstractmethod
from os.path import splitext, basename, join

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.db import models
from django.db.models.fields.files import FileField
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from unidecode import unidecode

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

    # Champs
    acl_mode = models.PositiveSmallIntegerField(default=PUBLIC, choices=ACL_MODES, verbose_name=_("Mode"))
    acl_custom = models.ForeignKey('content.customacl', null=True, verbose_name=_("ACL configuration"))

    # Getter
    def get_acl_directory(self):
        """ Renvoyer le nom de répertoire d'ACL pour l'objet """
        if self.acl_mode == self.REGISTERED:
            return self.ACL_PATHS[self.REGISTERED]
        elif self.acl_mode == self.PRIVATE:
            owner = self.get_acl_owner()
            return "{acl}/{spread}/{owner}".format(acl=self.ACL_PATHS[self.PRIVATE], owner=owner, spread=self._get_hash_path(owner))
        elif self.acl_mode == self.FRIENDS:
            owner = self.get_acl_owner()
            return "{acl}/{spread}/{owner}".format(acl=self.ACL_PATHS[self.FRIENDS], owner=owner, spread=self._get_hash_path(owner))
        elif self.acl_mode == self.CUSTOM:
            return self.acl_custom.get_acl_directory()
        else:
            return self.ACL_PATHS[self.PUBLIC]

    def get_acl_upload_path(self, filename, update=False):
        """
        Renvoyer le chemin d'upload du fichier

        :param self: instance d'objet. Hérite de préférence de DatetimeModel
        :param filename: nom du fichier uploadé. Peut être None
        :param update: indique que le fichier existait déjà et est resauvegardé
        """
        filename = unidecode(filename).lower() if filename else self.get_filename() if self else uuid_bits(64)
        filename = filename.split('?')[0].split('#')[0]
        filename = filename or uuid_bits(64)  # si le ? est au début de la chaîne, générer un nom de fichier
        # Créer les dictionnaires de données de noms de fichiers
        now = self.get_datetime() if self else timezone.now()
        fmt = now.strftime
        # Remplir le dictionnaire avec les informations de répertoire
        data = self.get_acl_upload_info()
        dir_info = {'year': fmt("%Y"), 'month': fmt("%m"), 'week': fmt("%W"), 'day': fmt("%d"), 'type': self._meta.model_name, 'acl': self.get_acl_directory()}
        name_info = {'name': slugify(splitext(basename(filename))[0]), 'ext': splitext(basename(filename))[1]}
        timestamp_info = {'hour': fmt("%H"), 'minute': fmt("%M"), 'second': fmt("%S"), 'week': fmt("%W")}
        data.update(dir_info)
        data.update(name_info)
        data.update(timestamp_info)
        # Renvoyer le répertoire ou le chemin complet du fichier (documenter)
        path = "".join(["test/" if settings.TEST else "",
                        "{acl}/{type}",
                        "/{year}/{month}{week}",
                        "/{author}/{name}{ext}" if not update else ""]
                       ).format(**data)
        return path

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
        Le chemin est calculé à partir des 24 premiers bits du hachage SHA1
        :returns: un sous-chemin de 3 répertoires, 6 caractères hexa.
        """
        digest = hashlib.sha1(name.encode('utf-8')).hexdigest()
        parts = [digest[idx:idx + 2] for idx in range(0, 6, 2)]
        return '/'.join(parts)

    def _is_file_path_obsolete(self):
        """ Renvoie si une mise à jour du chemin de fichier aura un quelconque effet """
        file_attribute = self.get_file_attribute()
        new_path = self.get_acl_upload_path(self.get_filename(extension=True), update=True)
        name_only, ext = splitext(self.get_filename(extension=True))
        filename = "{}{}".format(slugify(name_only), ext)
        output_file = join(new_path, filename)
        old_path = file_attribute.name
        target_path = self.get_acl_upload_path(output_file)
        return target_path != old_path

    # Action
    def update_file_path(self, force_name=None):
        """
        Déplacer l'image vers son chemin par défaut

        :param force_name: Forcer un nouveau nom de fichier
        :type force_name: str
        """
        if self.exists():
            # Supprimer les miniatures de l'image
            self.prepare_file_path_update()
            # Changer la position du fichier
            file_attribute = self.get_file_attribute()
            new_path = self.get_acl_upload_path(self.get_filename(extension=True), update=True)
            name_only, ext = splitext(self.get_filename(extension=True))
            name_only = force_name if force_name else name_only
            filename = "{}{}".format(slugify(name_only), ext)
            output_file = join(new_path, filename)
            old_path = file_attribute.name
            target_path = self.get_acl_upload_path(output_file)
            # Puis recréer l'image dans le nouveau chemin
            if target_path != old_path:  # https://docs.djangoproject.com/en/1.7/_modules/django/core/files/storage/#Storage.get_available_name
                with File(file_attribute) as original:
                    file_attribute.open()
                    file_attribute.save(output_file, original)
                    self.save(force_update=True)
                default_storage.delete(old_path)
                return True
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
        super(ACLModel, self).save(*args, **kwargs)
        if getattr(settings, 'CONTENT_ACL_AUTO_UPDATE_PATHS', False):
            if self._is_file_path_obsolete():
                self.update_file_path()

    # Métadonnées
    class Meta:
        permissions = [('can_define_%(class)s_acl', "Can define ACL configurations for %(class)s")]
        abstract = True
