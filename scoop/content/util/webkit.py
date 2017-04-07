# coding: utf-8
import sys
import time

try:
    import PyQt4.QtCore as QtCore
    import PyQt4.QtGui as QtGui
    import PyQt4.QtWebKit as QtWebKit
    from PyQt4.QtGui import QApplication
except ImportError:
    import PyQt5.QtCore as QtCore
    import PyQt5.QtGui as QtGui
    try:
        from PyQt5.QtWebKitWidgets import QWebView as WebView
    except ImportError:
        from PyQt5.QtWebEngineWidgets import QWebEngineView as WebView
    from PyQt5.QtWidgets import QApplication


class Screenshot(WebView):
    """
    Capture de pages web

    Exemple :
    >> s = Screenshot()
    >> s.capture('http://sitescraper.net', 'website.png', [1024, 0])
    >> s.capture('http://sitescraper.net/blog', '/home/john/blog.png')
    """

    def __init__(self):
        """ Initialiser le captureur d'URL """
        self.app = QApplication(sys.argv)
        WebView.__init__(self)
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
        self.load(QtCore.QUrl(url))
        self._wait_load()
        # Récupérer la frame document et créer un viewport de la taille du contenu
        frame = self.page().mainFrame()
        self.page().setViewportSize(QtCore.QSize(size[0], size[1] if size[1] >= 240 else frame.contentsSize().height()))
        # Créer une image Qt de la taille du viewport et y peindre le viewport
        image = QtGui.QImage(self.page().viewportSize(), QtGui.QImage.Format_ARGB32)
        painter = QtGui.QPainter(image)
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
