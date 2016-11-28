# coding: utf-8
"""
Processeurs d'image pour easy-thumbnails (smileychris)
voir : http://easy-thumbnails.readthedocs.org/en/latest/ref/processors/
ou : https://github.com/SmileyChris/easy-thumbnails
Tous ces processeurs utilisent les fonctionnalités d'image de PyQt4 et PIL
"""

from PIL import Image, ImageChops, ImageEnhance, ImageFilter
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QBrush, QColor, QImage, QPainter, QPen, QPolygon

BLUR_LEVELS = {'low': 2, 'medium': 8, 'high': 32}


def _pil_to_qt(image):
    """ Convertir une image PIL vers une image QT """
    width, height = image.size
    data = image.convert("RGBA").tobytes('raw', 'BGRA')
    qt_image = QImage(data, width, height, QImage.Format_ARGB32)
    return qt_image


def _qt_to_pil(image):
    """ Convertir une image QT vers une image PIL """
    size = (image.width(), image.height())
    data = image.bits().asstring(image.numBytes())
    pil_image = Image.frombuffer('RGBA', size, data, 'raw', 'BGRA', 0, 1)
    return pil_image


def _qt_canvas(image):
    """ Créer un canevas QT aux dimensions d'une image PIL """
    width, height = image.size
    newimage = QImage(width, height, QImage.Format_ARGB32)
    newimage.fill(QColor(0, 0, 0, 0))
    return newimage


def blurring(image, blur=False, **kwargs):
    """
    Appliquer un flou gaussien sur l'image

    :param image:
    :param blur: False, 'low', 'medium' ou 'high'
    :type blur: str | int
    """
    blur = BLUR_LEVELS.get(blur, blur)
    if blur and blur < 64:
        image = image.filter(ImageFilter.GaussianBlur(blur))
    return image


def pixelation(image, pixelate=False, **kwargs):
    """
    Appliquer une pixellisation de l'image avec un effet mosaique

    :param image:
    :param pixelate: False ou un nombre entre 2 et 32
    :return: Une image PIL pixellisée
    """
    if pixelate and 2 <= pixelate <= 32:
        width, height = image.size[0], image.size[1]
        image = image.resize((image.size[0] / pixelate, image.size[1] / pixelate), Image.LINEAR)
        image = image.resize((width, height), Image.NEAREST)
    return image


def channel_select(image, channel_r=False, channel_g=False, channel_b=False, **kwargs):
    """
    Appliquer un mélange des canaux R, V et B de l'image

    :param image:
    :param channel_r: Conserver le canal rouge
    :param channel_g: Conserver le canal vert
    :param channel_b: Conserver le canal bleu
    :return: Une image PIL dont 1 à 2 canaux manquent, sinon l'image originale
    """
    channels = [int(channel_r) * 255, int(channel_g) * 255, int(channel_b) * 255, 255]
    if channels not in ([0, 0, 0, 255], [255, 255, 255, 255]):
        width, height = image.size[0], image.size[1]
        mix_image = Image.new("RGBA", (width, height), color=tuple(channels))
        image = ImageChops.multiply(image.convert('RGBA'), mix_image)
    return image


def saturation(image, saturate=False, **kwargs):
    """
    Appliquer une saturation ou une désaturation de l'image

    :param image:
    :param saturate: False ou un nombre flottant positif
    :return: Une image PIL saturée si saturate est True ou > 1, et désaturée en dessous de 1
    """
    if saturate is True or isinstance(saturate, (int, float)):
        saturate = 2.0 if saturate is True else saturate
    if saturate is not False:
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(saturate)
    return image


def hexagon_mask(image, hexa=False, **kwargs):
    """
    Appliquer un découpage du masque de l'image en hexagone arrondi

    :param image: image PIL
    :param hexa: False ou le rayon des arrondis de l'hexagone en pixels
    :return: Une image PIL dont le contour est un haxagone aux angles arrondis ou l'image originale
    """
    if hexa is not False:
        try:
            qimage = _pil_to_qt(image)
            # Créer une image de la même taille que l'originale
            newimage = _qt_canvas(image)
            painter = QPainter(newimage)
            painter.setRenderHint(QPainter.Antialiasing, True)
            # Dessiner un hexagone
            offset = hexa * 2.0
            width, height, bottom, top, t, l = qimage.width() - offset * 2, qimage.height() - offset * 2, 0.759, 0.241, offset, offset
            points = [l + width / 2.0, t + 0, l + width, t + height * top, l + width, t + height * bottom,
                      l + width / 2.0, t + height, l + 0, t + height * bottom, l + 0, t + height * top]
            brush = QBrush(qimage)
            pen = QPen(brush, offset * 2.0, cap=Qt.RoundCap, join=Qt.RoundJoin)
            pen.setColor(QColor(0, 0, 0, 0))
            painter.setBrush(brush)
            painter.setPen(pen)
            painter.drawPolygon(QPolygon(points))
            painter.end()
            return _qt_to_pil(newimage)
        except Exception:
            return image
    else:
        return image


def rounded_corners(image, radius=0, **kwargs):
    """
    Appliquer un découpage du masque de l'image en rectangle arrondi

    :param image: image PIL
    :param radius: rayon en pixels des coins arrondis
    """
    if radius == "full" or isinstance(radius, (int, float)):
        qimage = _pil_to_qt(image)
        newimage = _qt_canvas(image)
        painter = QPainter(newimage)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QBrush(qimage))
        painter.setPen(QColor(0, 0, 0, 0))
        if radius == "full":  # découper en ellipse
            painter.drawEllipse(0, 0, qimage.width(), qimage.height())
        elif isinstance(radius, (int, float)):  # découper en rectangle arrondi
            painter.drawRoundedRect(0, 0, qimage.width(), qimage.height(), radius, radius)
        painter.end()
        return _qt_to_pil(newimage)
    return image


def draw_cross(image, crossed=False, **kwargs):
    """
    Dessiner une croix noire au milieu de l'image

    Croix noire d'épaisseur 16px aux extrémités arrondies, cernée
    d'un contour blanc de 3px d'épaisseur. (22px d'épaisseur totale)
    """
    if crossed is True:
        qimage = _pil_to_qt(image)
        painter = QPainter(qimage)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # Dessiner une croix
        cross_size = min([qimage.width(), qimage.height()]) / 4.0
        center = [qimage.width() / 2.0, qimage.height() / 2.0]
        # Dessiner la croix blanche
        qpen = QPen(QBrush(QColor(255, 255, 255, 255)), 22.0, cap=Qt.RoundCap)
        painter.setPen(qpen)
        painter.drawLine(center[0] - cross_size, center[1] - cross_size, center[0] + cross_size, center[1] + cross_size)
        painter.drawLine(center[0] + cross_size, center[1] - cross_size, center[0] - cross_size, center[1] + cross_size)
        # Dessiner la croix noire
        qpen = QPen(QBrush(QColor(0, 0, 0, 255)), 16.0, cap=Qt.RoundCap)
        painter.setPen(qpen)
        painter.drawLine(center[0] - cross_size, center[1] - cross_size, center[0] + cross_size, center[1] + cross_size)
        painter.drawLine(center[0] + cross_size, center[1] - cross_size, center[0] - cross_size, center[1] + cross_size)
        painter.end()
        return _qt_to_pil(qimage)
    else:
        return image


def lightening(image, lighten=False, **kwargs):
    """
    Appliquer un filtre lumineux sur l'image.

    L'éclairage est obtenu en mode de composition PLUS, avec une
    lumière de couleur légèrement jaune.

    :param image: image PIL
    :param lighten: False ou un float entre 0.0 (identité) et 1.0 (lumière max)
    """
    try:
        lighten_ = float(lighten)
    except ValueError:
        lighten_ = 0
    if lighten_ > 0:
        qimage = _pil_to_qt(image)
        painter = QPainter(qimage)
        painter.setCompositionMode(QPainter.CompositionMode_Plus)
        painter.fillRect(0, 0, qimage.width(), qimage.height(), QColor(255, 217, 161, lighten_ * 255.0))
        painter.end()
        return _qt_to_pil(qimage)
    else:
        return image
