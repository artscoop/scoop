# coding: utf-8
import psutil
from django import template
from scoop.core.util.stream.directory import Paths

register = template.Library()


@register.simple_tag
def project_path(*args):
    """ Renvoyer le chemin du répertoire du projet """
    return Paths.get_root_dir(*args)


@register.simple_tag
def cpu_load():
    """ Renvoyer l'utilisation processeur """
    return psutil.cpu_percent(interval=0, percpu=False)
