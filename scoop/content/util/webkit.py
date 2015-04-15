# coding: utf-8
from __future__ import absolute_import

import sys
import time

import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4.QtWebKit


class Screenshot(PyQt4.QtWebKit.QWebView):
    """
    Capture de pages web
    Exemple :
    >> s = Screenshot()
    >> s.capture('http://sitescraper.net', 'website.png', [1024, 0])
    >> s.capture('http://sitescraper.net/blog', '/home/john/blog.png')
    """

    def __init__(self):
        """ Initialiser le captureur d'URL """
        self.app = PyQt4.QtGui.QApplication(sys.argv)
        PyQt4.QtWebKit.QWebView.__init__(self)
        self._loaded = False
        self.loadFinished.connect(self._loadFinished)

    def capture(self, url, output_file, size=None):
        """
        Capturer l'image d'une page et l'enregistrer
        :param url: URL de la page
        :param output_file: chemin du fichier de sortie
        :param size: liste ou tuple des dimensions
        """
        size = size or [1024, 0]
        self.load(PyQt4.QtCore.QUrl(url))
        self._wait_load()
        # Récupérer la frame document et créer un viewport de la taille du contenu
        frame = self.page().mainFrame()
        self.page().setViewportSize(PyQt4.QtCore.QSize(size[0], size[1] if size[1] >= 240 else frame.contentsSize().height()))
        # Créer une image Qt de la taille du viewport et y peindre le viewport
        image = PyQt4.QtGui.QImage(self.page().viewportSize(), PyQt4.QtGui.QImage.Format_ARGB32)
        painter = PyQt4.QtGui.QPainter(image)
        frame.render(painter)
        painter.end()
        image.save(output_file)

    def _wait_load(self, delay=0):
        """ Attendre le chargement d'une page """
        while not self._loaded:
            self.app.processEvents()
            time.sleep(delay)
        self._loaded = False

    def _loadFinished(self, result):
        """ Signal que la page a fini de charger """
        self._loaded = True
