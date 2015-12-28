# coding: utf-8
from math import exp, log

from scoop.content.analysis.classifiers.base import BaseClassifier
from scoop.content.analysis.models.feature import Feature


class FisherClassifier(BaseClassifier):
    """ Classifieur Fisher """

    def get_category_probability(self, feature, category):
        """ Renvoyer la probabilité d'une catégorie, selon une caractéristique """
        feature_probability = self.get_feature_probability(feature, category)
        if feature_probability == 0:
            return 0
        frequency_sum = sum([self.get_feature_probability(feature, cat) for cat in self.get_categories()])
        probability = feature_probability / frequency_sum
        return probability

    def get_fisher_probability(self, document, category):
        """ Renvoyer la probabilité selon Fisher """
        probability = 1
        features = Feature.get_from_text(document)
        for feature in features:
            probability *= self.get_weighted_probability(feature, category, self.get_category_probability)
        feature_score = -2.0 * log(probability)
        return self.invchi2(feature_score, len(features) * 2)

    def invchi2(self, chi, df):
        """ Calcul de probabilité selon version lig2 """
        m = chi / 2.0
        total = term = exp(-m)
        for i in range(1, df // 2):
            term *= m / i
            total += term
        return min(total, 1.0)

    def set_threshold(self, category, value):
        """ Définir le seuil de probabilité pour accepter une catégorie """
        self.minimums[category] = value

    def get_threshold(self, category):
        """ Récupérer le seuil de probabilité de classement dans une catégorie """
        return self.minimums.get(category, 0)

    def guess(self, document, categories, default=None):
        """ Trouver la meilleure catégorie pour un document """
        # Loop through looking for the best result
        best = default
        maximum = 0.0
        for category in categories:
            probability = self.get_fisher_probability(document, category)
            # Make sure it exceeds its minimum
            if probability > self.get_threshold(category) and probability > maximum:
                best = category
                maximum = probability
        return best
