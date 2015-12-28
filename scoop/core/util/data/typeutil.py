# coding: utf-8
import hashlib

import webcolors


def str_to(value, newtype, default=0):
    """ Renvoyer une chaîne convertie en un autre type ou une valeur par défaut """
    try:
        return newtype(value)
    except:
        return default


def make_iterable(value, output_type=list):
    """ Renvoyer un type d'itérable depuis un objet seul ou un itérable """
    if isinstance(value, (list, set, tuple)):
        return output_type(value)
    return output_type([value]) if value is not None else output_type()


def hash_rgb(value):
    """ Renvoyer un hash de couleur depuis une chaîne """
    result = int(hashlib.md5(value).hexdigest(), 16)
    red, green, blue = (result / 65536) % 256, (result / 256) % 256, (result) % 256
    return red, green, blue


def closest_color(requested_color):
    """ Renvoyer la couleur CSS la plus proche d'une couleur RGB au format tuple """
    min_colors = dict()
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]


def get_color_name(requested_color):
    """ Renvoyer le nom de la couleur CSS la plus proche """
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_color)
    except ValueError:
        closest_name = closest_color(requested_color)
        actual_name = None
    return actual_name or "&#8776;{}".format(closest_name)


def list_contains(t, text):
    """ Renvoyer si un itérable de chaînes contient une sous-chaîne """
    for i in t:
        if text in i:
            return True
    return False


def is_multi_dimensional(value):
    """ Renvoyer si une liste ou un tuple contient des listes ou des tuples """
    if isinstance(value, (list, tuple)) and value:
        return isinstance(value[0], (list, tuple))
    return False
