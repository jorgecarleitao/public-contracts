import json

from django.db.models import Q
from django.core.cache import caches

from pt_law_parser import analyse, common_managers, observers, ObserverManager, \
    from_json, html_toc

from law.models import Document, Type


PLURALS = {'Decreto-Lei': 'Decretos-Leis',
           'Lei': 'Leis',
           'Portaria': 'Portarias'}

SINGULARS = {'Decretos-Leis': 'Decreto-Lei',
             'Leis': 'Lei',
             'Portarias': 'Portaria'}


def get_references(document, analysis=None):
    if analysis is None:
        analysis = text_analysis(document)

    query = Q()
    for name, number in analysis.get_doc_refs():
        type_name = name
        if name in SINGULARS:
            type_name = SINGULARS[name]
        query |= Q(type__name=type_name, number=number)

    return Document.objects.exclude(dr_series='II').filter(query)\
        .exclude(id=document.id).prefetch_related('type')


def _text_analysis(document):
    type_names = list(Type.objects.exclude(name__contains='(')
                      .exclude(dr_series='II').values_list('name', flat=True))
    type_names += [PLURALS[name] for name in type_names if name in PLURALS]

    managers = common_managers + [
        ObserverManager(dict((name, observers.DocumentRefObserver)
                             for name in type_names))]

    terms = {' ', '.', ',', '\n', 'n.os', '«', '»'}
    for manager in managers:
        terms |= manager.terms

    analysis = analyse(document.text, managers, terms)

    docs = get_references(document, analysis)

    mapping = {}
    for doc in docs:
        type_name = doc.type.name
        if doc.type.name in PLURALS:
            mapping[(PLURALS[doc.type.name], doc.number)] = doc.get_absolute_url()
        mapping[(type_name, doc.number)] = doc.get_absolute_url()

    analysis.set_doc_refs(mapping)

    return analysis


def text_analysis(document, flush=False):
    # short-circuit if no caching present
    if 'law_texts' not in caches:
        return _text_analysis(document)

    key = 'analyse_text>v%d>%d' % (1, document.dre_doc_id)
    cache = caches['law_texts']

    value = cache.get(key)
    if value and not flush:
        result = from_json(json.loads(value))
    else:
        result = _text_analysis(document)
        cache.set(key, json.dumps(result.as_json()))

    return result


def compose_index(document):
    analysis = text_analysis(document)

    return html_toc(analysis).as_html()
