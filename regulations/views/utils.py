#vim: set encoding=utf-8
from django.conf import settings
from django.core.urlresolvers import reverse

from regulations.generator import generator
from regulations.generator.layers.toc_applier import TableOfContentsLayer
from regulations.generator.layers.meta import MetaLayer


def get_layer_list(names):
    layer_names = generator.LayerCreator.LAYERS
    return set(l.lower() for l in names.split(',') if l.lower() in layer_names)


def table_of_contents(regulation_part, version, sectional=False):
    """ Generate a Table of Contents from the toc layer, without using a tree.
    We currently generate a section-level table of contents.  """

    layer_manager = generator.LayerCreator()
    layer_manager.add_layer(
        TableOfContentsLayer.shorthand, regulation_part, version, sectional)

    p_applier = layer_manager.appliers['paragraph']
    toc_layer = p_applier.layers[TableOfContentsLayer.shorthand]
    applied_layer = toc_layer.apply_layer(regulation_part)

    return applied_layer[1]


def regulation_meta(regulation_part, version, sectional=False):
    """ Return the contents of the meta layer, without using a tree. """

    layer_manager = generator.LayerCreator()
    layer_manager.add_layer(
        MetaLayer.shorthand, regulation_part, version, sectional)

    p_applier = layer_manager.appliers['paragraph']
    meta_layer = p_applier.layers[MetaLayer.shorthand]
    applied_layer = meta_layer.apply_layer(regulation_part)

    return applied_layer[1]


def handle_specified_layers(
        layer_names, regulation_id, version, sectional=False):

    layer_list = get_layer_list(layer_names)
    layer_creator = generator.LayerCreator()
    layer_creator.add_layers(layer_list, regulation_id, version, sectional)
    return layer_creator.get_appliers()


def handle_diff_layers(
        layer_names, regulation_id, older, newer, sectional=False):

    layer_list = get_layer_list(layer_names)
    layer_creator = generator.DiffLayerCreator(newer)
    layer_creator.add_layers(layer_list, regulation_id, older, sectional)
    return layer_creator.get_appliers()


def add_extras(context):
    if getattr(settings, 'JS_DEBUG', False):
        context['env'] = 'source'
    else:
        context['env'] = 'built'
    prefix = reverse('regulation_landing_view', kwargs={'label_id': '9999'})
    prefix = prefix.replace('9999', '')
    context['APP_PREFIX'] = prefix
    ga_settings = getattr(settings, 'EREGS_GA', {})

    for site in ga_settings:
        for val in ga_settings[site]:
            ga_index = "EREGS_GA_" + site + '_' + val
            context[ga_index] = ga_settings[site][val]

    if not 'EREGS_GA_EREGS_SITE' in context and not 'EREGS_GA_EREGS_ID' in context:
        for attr in ('GOOGLE_ANALYTICS_SITE', 'GOOGLE_ANALYTICS_ID'):
            new_index = attr.replace('GOOGLE_ANALYTICS', 'EREGS_GA_EREGS')
            context[new_index] = getattr(settings, attr, '')
    return context


def first_section(reg_part, version):
    """ Use the table of contents for a regulation, to get the label of the
    first section of the regulation. In most regulations, this is -1, but in
    some it's -101. """

    toc = table_of_contents(reg_part, version, sectional=False)

    if 'Subpart' in toc[0]['index']:
        return toc[0]['sub_toc'][0]['section_id']
    else:
        return toc[0]['section_id']
