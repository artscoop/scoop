# coding: utf-8
"""
Utilisation:
- Dans un template, ajouter {% enable_macros %}
- Utiliser un macro comme un block
- Repeat macro block
"""
from django import template
from django.template import Node, TemplateSyntaxError
from django.template.base import Parser
from django.template.loader_tags import BlockNode, do_block

register = template.Library()


class MacroRoot(Node):
    """ Nœud racine des macros, ajouter un _macro_root réutilisable par le parser """

    def __init__(self, nodelist=[]):
        """ Initialiser le nœud """
        self.nodelist = nodelist

    def render(self, context):
        """ Rendre les nœuds enfants """
        return self.nodelist.render(context)

    def find(self, block_name, parent_nodelist=None):
        """ Retrouver un block par son nom """
        if parent_nodelist is None:
            parent_nodelist = self.nodelist
        for node in parent_nodelist:
            if isinstance(node, (MacroNode, BlockNode)):
                if node.name == block_name:
                    return node
            if hasattr(node, 'nodelist'):
                result = self.find(block_name, node.nodelist)
                if result:
                    return result
        return None  # nothing found


class MacroNode(BlockNode):
    """ Nœud de macro/bloc, dont le contenu n'est rendu que via %repeat% """

    def render(self, context):
        """ Ne pas rendre le contenu de la macro """
        return ''

    def repeat(self, context):
        """ Renvoyer le contenu répété """
        return super(MacroNode, self).render(context)


class RepeatNode(template.Node):
    """ Nœud de répétition d'un nœud block ou macro """

    def __init__(self, block_name, macro_root, extra_context):
        """ Initialiser le nœud """
        self.block_name = block_name
        self.macro_root = macro_root
        self.extra_context = extra_context

    def render(self, context):
        """ Rendre le nœud """
        # Retrouver le bloc dont le nom est celui passé au bloc repeat
        block = self.macro_root.find(self.block_name)
        if not block:
            raise TemplateSyntaxError("cannot repeat '%s': block or macro not found" % self.block_name)
        else:
            # resolve extra context variables
            resolved_context = {}
            for key, value in self.extra_context.items():
                resolved_context[key] = value.resolve(context)
            # render the block with the new context
            context.update(resolved_context)
            if isinstance(block, MacroNode):
                result = block.repeat(context)
            else:
                result = block.render(context)
            context.pop()
            return result


@register.tag(name="enable_macros")
def do_enablemacros(parser, token):
    """ Activer les macros dans le template """
    # Vérifier l'absence d'arguments au tag
    bits = token.split_contents()
    if len(bits) != 1:
        raise TemplateSyntaxError("'%s' takes no arguments" % bits[0])
    # Ajouter l'objet MacroRoot au parser pour que les %repeat% fonctionnent
    parser._macro_root = MacroRoot()
    # Ajouter la liste des nœuds du parser à l'objet macro_root
    nodelist = parser.parse()
    if nodelist.get_nodes_by_type(MacroRoot):
        raise TemplateSyntaxError("'%s' cannot appear more than once in the same template" % bits[0])
    parser._macro_root.nodelist = nodelist
    return parser._macro_root


@register.tag(name="extends_with_macros")
def do_extends_with_macros(parser, token):
    """ Activer les macros avec les nœuds du template et de ses ancêtres """
    from django.template.loader_tags import do_extends
    # Ajouter un macroRoot dont la liste de nœuds est celle du extends
    parser._macro_root = MacroRoot()
    extendsnode = do_extends(parser, token)
    parser._macro_root.nodelist = extendsnode.nodelist
    return extendsnode


@register.tag(name="macro")
def do_macro(parser, token):
    """ Renvoyer un nœud macro """
    # Créer le nœud de bloc
    result = do_block(parser, token)
    # Et le transformer en bloc macro (ça marche, héritage direct)
    result.__class__ = MacroNode
    return result


@register.tag(name="repeat")
def do_repeat(parser, token):
    """ Renvoyer un bloc repeat """

    class RepeatTagParser(Parser):
        """ Parser de tag repeat """

        def top(self):
            extra_context = {}
            # first tag is the blockname
            try:
                block_name = self.tag()
            except TemplateSyntaxError:
                raise TemplateSyntaxError("'%s' requires a block or macro name" % self.tagname)
            # read param bindings
            while self.more():
                tag = self.tag()
                if tag == 'with' or tag == 'and':
                    value = self.value()
                    if self.tag() != 'as':
                        raise TemplateSyntaxError("variable bindings in %s must be 'with value as variable'" % self.tagname)
                    extra_context[self.tag()] = parser.compile_filter(value)
                else:
                    raise TemplateSyntaxError("unknown subtag %s for '%s' found" % (tag, self.tagname))
            return self.tagname, block_name, extra_context

    # Traiter le contenu du tag
    (tag_name, block_name, extra_context) = RepeatTagParser(token.contents).top()
    # return as a RepeatNode
    if not hasattr(parser, '_macro_root'):
        raise TemplateSyntaxError("'%s' requires macros to be enabled first" % tag_name)
    return RepeatNode(block_name, parser._macro_root, extra_context)
