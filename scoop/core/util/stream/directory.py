# coding: utf-8
from __future__ import absolute_import

import sys
from os.path import dirname, exists, join


class Paths(object):
    """ Classe utilitaire pour les chemins spécifiques au projet """

    @staticmethod
    def get_root_dir(*sublist):
        """ Renvoyer le chemin du répertoire du projet contant manage.py """
        try:
            import settings
            current_dir = dirname(settings.__file__)
            while not exists(join(current_dir, 'manage.py')) and len(current_dir) > 4:
                current_dir = dirname(current_dir)
            sublist += ('',)
            for item in sublist:
                current_dir = join(current_dir, item)
            return current_dir
        except ImportError:
            raise

    @staticmethod
    def get_python():
        """ Renvoyer le chemin de l'interpréteur python actuel """
        return sys.executable

    @staticmethod
    def is_isolated():
        """ Renvoyer si on est dans un environnement isolé type virtualenv """
        return hasattr(sys, 'real_prefix')
