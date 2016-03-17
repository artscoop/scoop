# coding: utf-8
import re

from textblob.classifiers import contains_extractor

REGEX_DIGIT_SEQUENCE_7 = r"(\d\s*){7}"  # Séquence de 7+ chiffres
REGEX_DIGIT_SEQUENCE_4 = r"(\d\s*){4}"  # Séquence de 4+ chiffres
REGEX_DIGIT_SEQUENCE_2 = r"(\d\s*){2}"  # Séquence de 2+ chiffres
REGEX_DIGIT_PRESENCE_7 = r"(\d.*){7}"  # Présence de 7+ chiffres au total
REGEX_CURRENCY_PRESENCE = r"((euro|dollar|yen)(s|[0-9]|\s|\W))|([€\$£¥])"
REGEX_EMAIL_MARKERS = r"(@|ar+ow?ba)"


def extractor_base(document, train_set=None):
    """ Renvoyer des propriétés du texte """
    features = contains_extractor(document, train_set)
    features['has_digit_sequence(7)'] = bool(re.search(REGEX_DIGIT_SEQUENCE_7, document))
    features['has_digit_sequence(4)'] = bool(re.search(REGEX_DIGIT_SEQUENCE_4, document))
    features['has_digit_sequence(2)'] = bool(re.search(REGEX_DIGIT_SEQUENCE_2, document))
    features['has_digits(7)'] = bool(re.search(REGEX_DIGIT_PRESENCE_7, document))
    features['has_curency()'] = bool(re.search(REGEX_CURRENCY_PRESENCE, document))
    features['has_email_markers()'] = bool(re.search(REGEX_EMAIL_MARKERS, document))
    return features
