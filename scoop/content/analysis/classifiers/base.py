# coding: utf-8
from django.db.models.aggregates import Sum
from scoop.content.analysis.models.category import Category
from scoop.content.analysis.models.statistics import CategoryCount, FeatureCount


class BaseClassifier(object):
    """ Base de Classifieur """

    def __init__(self, *args, **kwargs):
        """ Initialiser le classifieur """
        super(BaseClassifier, self).__init__(*args, **kwargs)

    def increment_feature_count(self, feature, category):
        """ Incrémenter le total d'une caractéristique """
        count = FeatureCount.get(feature, category)
        FeatureCount.set(feature, category, count + 1)

    def get_feature_count(self, feature, category):
        """ Récupérer le total d'une caractéristique dans une catégorie """
        return FeatureCount.get(feature, category)

    def increment_category_count(self, category):
        """ Incrémenter le total de caractéristiques dans une catégorie """
        count = CategoryCount.get(category)
        CategoryCount.set(category, count + 1)

    def get_category_count(self, category):
        """ Récupérer le total de caractéristiques dans une catégorie """
        return CategoryCount.get(category)

    def get_categories(self):
        """ Récupérer la liste des catégories """
        return Category.objects.all()

    def get_total_features(self):
        """ Récupérer le total de caractéristiques, toutes catégories confondues """
        return CategoryCount.objects.all().aggregate(Sum('total'))['total__sum']

    def learn(self, document, category):
        """ Entraîner le classifieur en classant un contenu """
        from scoop.content.analysis.models.document import Document
        from scoop.content.analysis.models.feature import Feature

        document = Document.set(document, category)
        features = Feature.get_from_text(document)
        for feature in features:
            FeatureCount.increment(feature, category)
        CategoryCount.increment(category)

    def get_feature_probability(self, feature, category):
        """ Renvoyer la probabilité d'une caractéristique """
        category_count, feature_count = self.get_category_count(category), self.get_feature_count(feature, category)
        return (feature_count / category_count) if category_count > 0 else 0

    def get_weighted_probability(self, feature, category, probability_function, weight=1.0, assumed_probability=0.5):
        """ Renvoyer la probabilité (??) """
        basic_probability = probability_function(feature, category)
        totals = self.get_total_features()
        balanced_probability = ((weight * assumed_probability) + (totals * basic_probability)) / (weight + totals)
        return balanced_probability
