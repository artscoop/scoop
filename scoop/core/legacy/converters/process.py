# coding: utf-8
import gc
import time


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
        start_index = cls.importers.index(cls.start_with) if cls.start_with else 0
        importers = cls.importers[start_index:]
        start = time.time()
        if cls.setup() is True:
            if cls.importers and isinstance(cls.importers, list):
                # Import première passe
                importers = [importer() for importer in importers]
                count = len(importers)
                # Import première passe
                for ind, importer in enumerate(importers, start=1):
                    print("Importing model {ind}/{count} using {name}".format(ind=ind, count=count, name=importer.__class__.__name__))
                    i_start = time.time()
                    importer.imports()
                    i_elapsed = time.time() - i_start
                    gc.collect()
                    print("Model successfully imported in {:.01f}s.".format(i_elapsed))
                # Import deuxième passe
                for ind, importer in enumerate(importers, start=1):
                    print("Updating imports {ind}/{count} using {name}".format(ind=ind, count=count, name=importer.__class__.__name__))
                    i_start = time.time()
                    importer.post_imports()
                    i_elapsed = time.time() - i_start
                    gc.collect()
                    print("Model successfully updated in {:.01f}s.".format(i_elapsed))
                # Import troisième passe
                for ind, importer in enumerate(importers, start=1):
                    print("Finishing {ind}/{count} using {name}".format(ind=ind, count=count, name=importer.__class__.__name__))
                    i_start = time.time()
                    importer.brushup()
                    i_elapsed = time.time() - i_start
                    gc.collect()
                    print("End of model process updated in {:.01f}s.".format(i_elapsed))
                # Touche de fin
                cls.brushup()
                elapsed = time.time() - start
                minute, second = divmod(elapsed, 60)
                print("*" * 80)
                print("Import completed in {min:.0f}m{sec:.0f}s.".format(min=minute, sec=second))
