# coding: utf-8


def round_left(value, digits=1):
    """
    Arrondir un nombre aux n chiffres les plus significatifs

    Exemples :
    >> round_left(1499, 2)
    1500
    >> round_left(1494, 3)
    1490
    >> round_left(19.1234, 4)
    19.12

    :param digits: nombre de chiffres significatifs
    :param value: valeur à arrondir
    """
    result = float("{{:.{0}g}}".format(abs(digits)).format(value))
    return int(result) if result == int(result) else result
