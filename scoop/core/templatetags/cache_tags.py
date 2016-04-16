# coding: utf-8
from django import template
from django.core.cache import cache
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def cache_at(request, key):
    """ Renvoyer la valeur en cache à la clé *key* """
    value = cache.get(key)
    if isinstance(value, str):
        return mark_safe(value)
    return ''
