# coding: utf-8
import io
import pickle
import pprint
import time
from os.path import join

from django.db.models.base import Model
from scoop.core.util.stream.directory import Paths


class DocumentExporter(object):
    """ Mixin d'export de documents """
    name = None  # Nom de fichier à enregistrer (sans extension)

    # Utilitaire
    def instance_for_ct(self, ct, oi):
        """
        Renvoyer une instance d'objet depuis un type de contenu et un id

        :param ct: instance ContentType
        :param oi: id de l'instance d'obet
        """
        raise NotImplementedError("Should return an instance from the content type and object id")

    def modelname_for_ct(self, ct):
        """
        Renvoyer le nom du modèle pour un type de contenu

        :param ct: instance ContentType
        """
        raise NotImplementedError("Should return a model name from the content type and object id")

    def get_fields_data(self, obj, *fields):
        """
        Renvoyer les données des champs d'un objet

        :param obj: instance de modèle
        :param fields: liste de champs à exporter dans le dictionnaire de sortie
        :rtype: dict
        """
        output = dict()
        for field in fields:
            if hasattr(obj, field):
                value = getattr(obj, field)
                try:
                    output[field] = value if not isinstance(value, Model) else str(value)
                except UnicodeEncodeError:
                    raise
        return output

    def get_generic_data(self, obj, representation=None, ct=None, oi=None):
        """
        Renvoyer une représentation dictionnaire d'une GenericForeignKey

        :param obj: instance dont on retrouve les infos de GenericForeignKey
        :param representation: chaîne représentant l'objet ciblé par *obj*. None pour utiliser la représentation par défaut.
        :param ct: nom du champ ciblant un ContentType
        :param oi: nom du champ contenant l'ID de l'objet cible
        """
        ct = ct or 'content_type_id'
        oi = oi or 'object_id'
        if getattr(obj, ct, None) is not None:
            typename = self.modelname_for_ct(getattr(obj, ct))
            item = self.instance_for_ct(typename, getattr(obj, oi))
            output = {'type': typename, 'item': representation or str(item) if item else None}
        else:
            output = None
        return output

    def get_foreign_data(self, obj, attribute):
        """
        Renvoyer la représentation texte d'un objet en clé étrangère

        :param obj: instance de modèle
        :param attribute: nom du champ de clé étrangère
        """
        if getattr(obj, attribute, None) is not None:
            return str(getattr(obj, attribute))
        return None

    # Getter
    def get_export_list(self):
        """ Renvoyer une liste des objets à exporter """
        raise NotImplementedError("This method should return the list of all objects to export in one model")

    def get_object_export_data(self, obj):
        """ Renvoyer les données à exporter pour un objet (dictionnaire) """
        raise NotImplementedError("This method should return a dictionary of object data")

    # Setter
    def exports(self, name=None, debug=False):
        """
        Exporter les données dans un fichier

        :param name: nom du fichier de sortie
        :param debug: écrire également un fichier de sortie lisible par un humain
        """
        # Créer les données de sortie
        start = time.time()
        data = [self.get_object_export_data(item) for item in self.get_export_list() if item is not None]
        elapsed = time.time() - start
        # Écrire le fichier
        path = join(Paths.get_root_dir('files', 'legacy'), '{}.pickle'.format(name or self.name))
        with open(path, 'wb') as f:
            pickle.dump(data, f, protocol=3)
        # Écrire un autre fichier pretty printed
        if debug:
            with io.open("{}.txt".format(path), "w", encoding="utf-8") as f:
                pp = pprint.PrettyPrinter(stream=f)
                output = pp.pformat(data)
                f.write(str(output))
        # Résumé de l'opération
        print("- {exporter} successfully exported {count} items in {elapsed:.03f}s".format(exporter=type(self).__name__, count=len(data), elapsed=elapsed))


class DocumentImporter(object):
    """ Mixin d'import de document """
    name = None  # Nom de fichier à lire (sans extension)

    # Getter
    def progress(self, ind, total, every=None, label=None):
        """ Afficher la progression d'un opération """
        every = every or int(total / 25)
        if ind % every == 0:
            percent = ind * 100.0 / total
            print("{label} - Progress - {pc:.01f}%".format(pc=percent, label=label or "Import"))
        if ind == total - 1:
            print("{label} - Done".format(label=label or "Import"))

    def get_data(self, name=None):
        """ Renvoyer les données du fichier exporté """
        path = join(Paths.get_root_dir('files', 'legacy'), '{}.pickle'.format(name or self.name))
        with io.open(path, 'rb') as f:
            data = pickle.load(f)
        return data

    def get_data_fields(self, item, *fields):
        """ Renvoyer un dictionnaire de champs d'un élément du document """
        return {field: item[field] for field in fields}

    def get_generic_data(self, ct, oi):
        """ Renvoyer une instance d'objet via un type de contenu et un id """
        raise NotImplementedError()

    # Propriétés
    data = property(get_data)

    # Actions
    def imports(self, name=None):
        """ Importer le document dans la nouvelle base """
        raise NotImplementedError("This method creates instances from imported data")

    def post_imports(self, name=None):
        """ Traiter la seconde passe d'import """
        return

    def brushup(self, name=None):
        """ Traiter la dernière passe """
        return
