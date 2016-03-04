# coding: utf-8
from django.db.models.base import Model
from django.forms.forms import Form
from django.http.request import HttpRequest
from scoop.core.util.django.formutil import form
from scoop.user.models.forms import FormConfiguration


class DataForm(Form):
    """
    Classe de base de formulaire destiné à la sauvegarde de configurations utilisateur

    (voir user.models.FormConfiguration)
    Note: ne jamais changer le type d'un champ de formulaire.
    :cvar name: nom du formulaire, unique
    :cvar defaults: dictionnaire des valeurs par défaut des attributs champs
    :cvar saved_fields: liste des noms de champs qui seront les seuls à être mémorisés
    """

    # Configuration
    name = ''  # nom unique. minuscules et .
    defaults = None  # données par défaut
    saved_fields = None  # champs enregistrés. None pour tous les champs

    # Actions
    @classmethod
    def create(cls, request):
        """ Créer un formulaire depuis les données de requête, ou utiliser les données par défaut """
        return form(cls, request, cls.get_data_for(request.user))

    @classmethod
    def create_template(cls, template):
        """ Créer un formulaire depuis les données de requête, ou utiliser un template """
        return form(cls, None, cls.get_data_for(None, template))

    @classmethod
    def reset(cls, user, version=None):
        """ Supprimer les données de formulaire de la base et revenir aux valeurs par défaut """
        FormConfiguration.objects.filter(user=user, name=cls.name, version=version or "").delete()

    # Getter
    @classmethod
    def get_defaults(cls, user):
        """
        Renvoyer le dictionnaire par défaut des valeurs de formulaire

        Note : cette fonction peut être redéfinie pour renvoyer des valeurs
        par défaut adaptées à chaque utilisateur.
        """
        return cls.defaults

    @classmethod
    def get_option_for(cls, user, field, version=None):
        """
        Renvoyer la valeur stockée d'un champ du formulaire pour un utilisateur
        et dans une version nommée ou la version par défaut

        :param user: utilisateur pour lequel récupérer l'option
        :param field: nom du champ de formulaire pour lequel récupérer la valeur
        :param version: version du formulaire enregistré pour l'utilisateur, ou None
        """
        return cls.get_data_for(user, version=version).get(field, None)

    @classmethod
    def get_data_for(cls, user, version=None):
        """
        Renvoyer le dictionnaire de données initiales de fomulaire pour un utilisateur

        :param user: utilisateur pour lequel récupérer des données
        :param version: version des données à récupérer
        """
        if user is not None:
            user = user.user if isinstance(user, HttpRequest) else user
            if not user.is_authenticated():
                return {}
        result, defaults = dict(), cls.get_defaults(user)
        if isinstance(defaults, dict):
            result.update(defaults)
        data = FormConfiguration.objects.get_user_config(user, cls.name, version=version) if user else FormConfiguration.objects.get_template_config(cls.name, version=version)
        data = cls._fix_data(data)
        result.update(data)
        return result or None

    @classmethod
    def is_data_default(cls, user, version=None):
        """ Renvoyer si les données pour l'utilisateur et la version sont celles par défaut """
        return cls.get_data_for(user, version) == cls.get_defaults(user)

    @classmethod
    def is_option_default(cls, user, field, version=None):
        """ Renvoyer si une valeur de champ pour un utilisateur et la version est à sa valeur par défaut """
        return cls.get_option_for(user, version) == cls.get_defaults(user).get(field, None)

    @classmethod
    def _fix_data(cls, data):
        """
        Remplacer les instances de Model en leurs clés primaires

        Raison : Il n'est pas toujours possible d'utiliser une instance de Model dans une initial_value
        """
        if not isinstance(data, dict):
            return dict()
        for key, value in data.items():
            # Dans le cas où la valeur n'est pas multiple (valeur seule)
            if isinstance(value, Model):
                data[key] = value.pk
            # Si la valeur est multiple (liste de valeurs)
            if isinstance(value, (list, tuple)):
                for idx, item in enumerate(value):
                    if isinstance(item, Model):
                        data[key][idx] = item.pk
        return data

    # Setter
    @classmethod
    def select_version(cls, user, version):
        """ Remplacer les donées actuelles de l'utilisateur par celles d'une autre version """
        try:
            versioned = FormConfiguration.objects.get(name=cls.name, user=user, version=version)
            FormConfiguration.objects.filter(name=cls.name, user=user, version="").delete()
            versioned.version = ""
            versioned.save()
        except FormConfiguration.DoesNotExist:
            pass

    @classmethod
    def set_option_for(cls, user, field, value, version=None):
        """ Modifier l'état d'un champ de données de formulaire pour un utilisateur """
        state = cls.get_data_for(user, version)
        state[field] = value
        FormConfiguration.objects.set_user_config(user, cls.name, state, version=version)

    def save_configuration(self, user=None, version=""):
        """
        Enregistrer les données de champs du formulaire
        dans les données d'utilisateur et pour la version désirée
        Nécessite l'appel de is_valid() au préalable
        """
        if user.is_authenticated():
            if hasattr(self, 'cleaned_data'):
                output = {key: value for key, value in self.cleaned_data.items() if (not self.saved_fields or key in self.saved_fields)}
                FormConfiguration.objects.set_user_config(user, self.name, output, version=version)
