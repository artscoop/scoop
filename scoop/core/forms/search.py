# coding: utf-8
from functools import reduce

from django import forms
from django.conf import settings
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.text import smart_split
from django.utils.translation import ugettext_lazy as _

# Liste statique de mots vides/stopwords
STOPWORDS_FR = "-elle,-il,10ème,1er,1ère,2ème,3ème,4ème,5ème,6ème,7ème,8ème,9ème,a,afin,ai,ainsi,ais,ait,alors," \
               "après,as,assez,au,aucun,aucune,auprès,auquel,auquelles,auquels,auraient,aurais,aurait,aurez,auriez," \
               "aurions,aurons,auront,aussi,aussitôt,autre,autres,aux,avaient,avais,avait,avant,avec,avez,aviez," \
               "avoir,avons,ayant,beaucoup,c',car,ce,ceci,cela,celle,celles,celui,cependant,certes,ces,cet,cette," \
               "ceux,chacun,chacune,chaque,chez,cinq,comme,d',d'abord,dans,de,dehors,delà,depuis,des,dessous,dessus," \
               "deux,deça,dix,doit,donc,dont,du,durant,dès,déjà,elle,elles,en,encore,enfin,entre,er,est,est-ce,et," \
               "etc,eu,eurent,eut,faut,fur,hormis,hors,huit,il,ils,j',je,jusqu',l',la,laquelle,le,lequel,les," \
               "lesquels,leur,leurs,lors,lorsque,lui,là,m',mais,malgré,me,melle,mes,mm,mme,moi,moins,mon,mr,même," \
               "mêmes,n',neuf,ni,non-,nos,notamment,notre,nous,néanmoins,nôtres,on,ont,ou,où,par,parce,parfois," \
               "parmi,partout,pas,pendant,peu,peut,peut-être,plus,plutôt,pour,pourquoi,près,puisqu',puisque,qu'," \
               "quand,quant,quatre,que,quel,quelle,quelles,quelqu',quelque,quelquefois,quelques,quels,qui,quoi,quot," \
               "s',sa,sans,se,sept,sera,serai,seraient,serais,serait,seras,serez,seriez,serions,serons,seront,ses,si," \
               "sien,siennes,siens,sitôt,six,soi,sommes,son,sont,sous,souvent,suis,sur,t',toi,ton,toujours,tous,tout," \
               "toutefois,toutes,troiw,tu,un,une,unes,uns,voici,voilà,vos,votre,vous,vôtres,y,à,ème,étaient,étais," \
               "était,étant,étiez,étions,êtes,être,afin,ainsi,alors,après,aucun,aucune,auprès,auquel,aussi,autant," \
               "aux,avec,car,ceci,cela,celle,celles,celui,cependant,ces,cet,cette,ceux,chacun,chacune,chaque,chez," \
               "comme,comment,dans,des,donc,donné,dont,duquel,dès,déjà,elle,elles,encore,entre,étant,etc,été,eux," \
               "furent,grâce,hors,ici,ils,jusqu,les,leur,leurs,lors,lui,mais,malgré,mes,mien,mienne,miennes,miens," \
               "moins,moment,mon,même,mêmes,non,nos,notre,notres,nous,notre,oui,par,parce,parmi,plus,pour,près,puis," \
               "puisque,quand,quant,que,quel,quelle,quelque,quelquun,quelques,quels,qui,quoi,sans,sauf,selon,ses," \
               "sien,sienne,siennes,siens,soi,soit,sont,sous,suis,sur,tandis,tant,tes,tienne,tiennes,tiens,toi,ton," \
               "tous,tout,toute,toutes,trop,très,une,vos,votre,vous,étaient,était,étant,être"
STOPWORDS_EN = 'a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,' \
               'cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,' \
               'his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,' \
               'no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,' \
               'that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,' \
               'which,while,who,whom,why,will,with,would,yet,you,your'
DEFAULT_STOPWORDS = STOPWORDS_FR + STOPWORDS_EN

# Récupérer le nom du moteur de base de données actuel
if settings.DATABASES:
    DATABASE_ENGINE = settings.DATABASES[list(settings.DATABASES.keys())[0]]['ENGINE'].split('.')[-1]
else:
    DATABASE_ENGINE = settings.DATABASE_ENGINE


class BaseSearchForm(forms.Form):
    """
    Formulaire de base de recherche de texte dans plusieurs champs

    La classe dérivant de celle-ci doit contenir une sous-classe Meta
    contenant les champs suivants :
    - base_qs : Queryset minimum (avec le maximum d'objets), ex. Class.objects
    - search_fields : Liste d'attributs dans lesquels effectuer la recherche
    """

    # Constantes
    STOPWORD_LIST = DEFAULT_STOPWORDS.split(',')
    DEFAULT_OPERATOR = Q.__and__

    # Champs
    q = forms.CharField(label=_("Search"), required=False)
    order_by = forms.CharField(widget=forms.HiddenInput(), required=False)

    # Validation
    def clean_q(self):
        """ Valider et renvoyer les données du champ de requête """
        return self.cleaned_data['q'].strip()

    def construct_search(self, field_name, first):
        """ Confectionner la requête de recherche """
        if field_name.startswith('^'):
            if first:
                return "%s__istartswith" % field_name[1:]
            else:
                return "%s__icontains" % field_name[1:]
        elif field_name.startswith('='):
            return "%s__iexact" % field_name[1:]
        elif field_name.startswith('@'):
            if DATABASE_ENGINE == 'mysql':
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name[1:]
        else:
            return "%s__icontains" % field_name

    def get_text_query_bits(self, query_string):
        """filter stopwords but only if there are useful words """
        split_q = list(smart_split(query_string))
        filtered_q = []
        for bit in split_q:
            if bit not in self.STOPWORD_LIST:
                filtered_q.append(bit)
        if len(filtered_q):
            return filtered_q
        else:
            return split_q

    def get_text_search_query(self, query_string):
        """ Renvoyer la requête utilisée pour query_string """
        filters = []
        first = True
        for bit in self.get_text_query_bits(query_string):
            or_queries = [Q(**{self.construct_search(str(field_name), first): bit}) for field_name in self.Meta.search_fields]
            filters.append(reduce(Q.__or__, or_queries))
            first = False
        if len(filters):
            return reduce(self.DEFAULT_OPERATOR, filters)
        else:
            return False

    def construct_filter_args(self, cleaned_data):
        """ Calculer les arguments de filtrage """
        args = []

        # if its an instance of Q, append to filter args
        # otherwise assume an exact match lookup
        for field in cleaned_data:
            if hasattr(self, 'prepare_%s' % field):
                q_obj = getattr(self, 'prepare_%s' % field)()
                if q_obj:
                    args.append(q_obj)
            elif isinstance(cleaned_data[field], Q):
                args.append(cleaned_data[field])
            elif field == 'order_by':
                pass  # special case - ordering handled in get_result_queryset
            elif cleaned_data[field]:
                if isinstance(cleaned_data[field], list) or isinstance(cleaned_data[field], QuerySet):
                    args.append(Q(**{field + '__in': cleaned_data[field]}))
                else:
                    args.append(Q(**{field: cleaned_data[field]}))

        return args

    def get_result_queryset(self):
        """ Renvoyer le queryset final """
        qs = self.Meta.base_qs
        cleaned_data = self.cleaned_data.copy()
        query_text = cleaned_data.pop('q', None)

        qs = qs.filter(*self.construct_filter_args(cleaned_data))

        if query_text:
            fulltext_indexes = getattr(self.Meta, 'fulltext_indexes', None)
            if DATABASE_ENGINE == 'mysql' and fulltext_indexes:
                # cross-column fulltext search if db is mysql, otherwise use default behaviour.
                # We're assuming the appropriate fulltext index has been created
                match_bits = []
                params = []
                for index in fulltext_indexes:
                    match_bits.append('MATCH(%s) AGAINST (%%s) * %s' % index)
                    params.append(query_text)

                match_expr = ' + '.join(match_bits)

                qs = qs.extra(
                    select={'relevance': match_expr},
                    where=(match_expr,),
                    params=params,
                    select_params=params,
                    order_by=('-relevance',)
                )

            else:
                # construct text search for sqlite, or for when no fulltext indexes are defined
                text_q = self.get_text_search_query(query_text)
                if text_q:
                    qs = qs.filter(text_q)
                else:
                    qs = qs.none()

        if self.cleaned_data['order_by']:
            qs = qs.order_by(*self.cleaned_data['order_by'].split(','))

        return qs.distinct()

    # Métadonnées
    class Meta:
        abstract = True
        base_qs = None
        search_fields = None  # ex: ['name', 'category__name', '@description', '=id']
        fulltext_indexes = None  # ex: [('field1,field2...', INT_WEIGHT), ...]
