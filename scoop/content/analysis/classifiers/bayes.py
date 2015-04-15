# coding: utf-8
from __future__ import absolute_import

from scoop.content.analysis.classifiers.base import BaseClassifier
from scoop.content.analysis.models.feature import Feature


class NaiveBayesClassifier(BaseClassifier):
    """ Classifieur Bayes """

    def __init__(self, *args, **kwargs):
        """ Initialiser le classifieur """
        super(NaiveBayesClassifier, self).__init__(*args, **kwargs)

    def get_document_probability(self, document, category):
        """ Renvoyer la probabilité qu'un document appartienne à une catégorie """
        features, probability = Feature.get_from_text(document), 1
        for feature in features:
            probability *= self.get_weighted_probability(feature, category, self.get_feature_probability)
        return probability

    def get_probability(self, document, category):
        """ Renvoyer la probabilité que ??? """
        category_probability = self.get_category_count(category) / self.get_total_features()
        document_probability = self.get_document_probability(document, category)
        return document_probability * category_probability

    def set_threshold(self, category, threshold=0.8):
        """ Définir le seuil de probabilité pour considérer une catégorie """
        self.thresholds[category] = threshold

    def get_threshold(self, category):
        """ Récupérer le seuil de probabilité de classement dans une catégorie """
        return self.thresholds[category] if category in self.thresholds else 1.0

    def guess(self, document, categories, default=None):
        """ Trouver la meilleure catégorie pour un document """
        probabilities = {}
        # Find the category with the highest probability
        highest = 0.0
        for category in categories:
            probabilities[category] = self.get_probability(document, category)
            if probabilities[category] > highest:
                highest = probabilities[category]
                best = category
        for category in probabilities:
            if category == best:
                continue
            if probabilities[category] * self.get_threshold(best) > probabilities[best]:
                return default
            return best
