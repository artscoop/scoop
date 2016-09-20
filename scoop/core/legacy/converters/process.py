# coding: utf-8
import gc
import threading
import time

import sys
from django.db import transaction


class ExportProcessor(object):
    """ Exporteur de plusieurs documents """

    exporters = None  # liste de classes d'exporteurs de documents
    start_with = None  # classe exporter

    @classmethod
    def exports(cls):
        """ Exporter les données """
        if cls.exporters and isinstance(cls.exporters, list):
            start = time.time()
            start_index = cls.exporters.index(cls.start_with) if cls.start_with else 0
            exporters = cls.exporters[start_index:]
            count = len(exporters)
            for ind, exporter in enumerate(exporters, start=1):
                print("Exporting model {ind}/{count} using {name}".format(ind=ind, count=count, name=exporter.__name__))
                exporter().exports()
                gc.collect()
            elapsed = time.time() - start
            minute, second = divmod(elapsed, 60)
            print("*" * 80)
            print("Export complete in {min:.0f}m{sec:.0f}s.".format(min=minute, sec=second))


class ImportProcessor(object):
    """ Importeur de documents """
    importers = None  # liste de classes d'importeurs de documents
    start_with = None  # commencer l'import depuis un importeur

    # Actions préparatoires
    @classmethod
    def setup(cls):
        """
        Préparer l'environnement d'import

        :returns: True si ok
        :rtype: bool
        """
        pass

    @classmethod
    def brushup(cls):
        """
        Actions sur la base après l'import

        Fignoler l'import avec des calculs ou autres process de fin d'import
        """
        pass

    @classmethod
    def imports(cls):
        """ Importer les documents dans la base """

        def _update_time(start):
            """ Afficher le temps écoulé depuis start """
            while _update_time.running is True:
                elapsed = time.time() - start
                minute, second = divmod(elapsed, 60)
                print("\x1b[s\x1b[1;0H\x1b[K\x1b[31;47m{min:02n}:{sec:02n}\x1b[u\x1b[0m".format(min=minute, sec=int(second)), end='')
                sys.stdout.flush()
                time.sleep(0.25)

        _update_time.running = True  # Autoriser le thread à boucler
        start_index = cls.importers.index(cls.start_with) if cls.start_with else 0
        importers = cls.importers[start_index:]
        start = time.time()
        t = threading.Thread(target=_update_time, args=[start])
        t.start()
        setup_cleared = cls.setup()
        if setup_cleared is True:
            if cls.importers and isinstance(cls.importers, list):
                # Import première passe
                importers = [importer() for importer in importers]
                count = len(importers)
                # Import première passe
                for ind, importer in enumerate(importers, start=1):
                    with transaction.atomic():
                        print("Importing model {ind}/{count} using {name}".format(ind=ind, count=count, name=importer.__class__.__name__))
                        i_start = time.time()
                        importer.imports()
                        i_elapsed = time.time() - i_start
                        print("Model successfully imported in {:.01f}s.".format(i_elapsed))
                # Import deuxième passe
                for ind, importer in enumerate(importers, start=1):
                    with transaction.atomic(savepoint=False):
                        print("Updating imports {ind}/{count} using {name}".format(ind=ind, count=count, name=importer.__class__.__name__))
                        i_start = time.time()
                        importer.post_imports()
                        i_elapsed = time.time() - i_start
                        print("Model successfully updated in {:.01f}s.".format(i_elapsed))
                        gc.collect()
                # Import troisième passe
                for ind, importer in enumerate(importers, start=1):
                    with transaction.atomic(savepoint=False):
                        print("Finishing {ind}/{count} using {name}".format(ind=ind, count=count, name=importer.__class__.__name__))
                        i_start = time.time()
                        importer.brushup()
                        i_elapsed = time.time() - i_start
                        print("End of model process updated in {:.01f}s.".format(i_elapsed))
                        gc.collect()
                # Touche de fin
                with transaction.atomic(savepoint=False):
                    i_start = time.time()
                    cls.brushup()
                    i_elapsed = time.time() - i_start
                    print("Last bit of process updated in {:.01f}s.".format(i_elapsed))
                _update_time.running = False  # Demander au thread de quitter
                elapsed = time.time() - start
                minute, second = divmod(elapsed, 60)
                print("*" * 80)
                print("Import completed in {min:.0f}m{sec:.0f}s.".format(min=minute, sec=second))
