# coding: utf-8


def round_left(value, digits=1):
    """ Arrondir un nombre aux n chiffres les plus significatifs """
    result = float("{{:.{}g}}".format(abs(digits)).format(value))
    return int(result) if result == int(result) else result
