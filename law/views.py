from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page

from . import models
from .forms import LawSelectorForm

import law.analysis


def build_laws_list_context(context, GET):
    """
    Uses parameters GET (from a request) to modify the context
    of deputies lists.

    Validates GET using ``LawSelectorForm``, and uses the ``cleaned_data``
    to apply search and ordering to ``context['laws']``.

    Returns the modified context.
    """
    page = GET.get(_('page'))

    context['selector'] = LawSelectorForm(GET)
    if context['selector'].is_valid():
        GET = context['selector'].cleaned_data
    else:
        GET = {}

    key = 'search'
    if key in GET and GET[key]:
        context['laws'] = context['laws'].filter(text__search=GET[key])

    paginator = Paginator(context['laws'], 20)
    try:
        context['laws'] = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        context['laws'] = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        context['laws'] = paginator.page(paginator.num_pages)

    return context


def home(request):
    return render(request, "law/home.html")


@cache_page(60 * 60 * 24)
def law_list(request):
    context = {'laws': models.Document.laws
                             .order_by("-dre_doc_id")
                             .prefetch_related("type")}

    context = build_laws_list_context(context, request.GET)

    context['navigation_tab'] = 'documents'

    return render(request, "law/law_list/main.html", context)


@cache_page(60 * 60 * 24)
def types_list(request):
    types = models.Type.objects.exclude(id__in=[95, 97, 145, 150]).annotate(count=Count('document')).order_by('name')

    context = {'types': types, 'navigation_tab': 'types'}

    return render(request, "law/type_list/main.html", context)


def type_view(request, type_id, slug=None):
    type = get_object_or_404(models.Type, id=type_id)

    context = {'type': type,
               'laws': type.document_set.order_by("-date", "-number").prefetch_related("type"),
               'navigation_tab': 'types'}

    context = build_laws_list_context(context, request.GET)

    return render(request, "law/type_view/main.html", context)


@cache_page(60 * 60 * 24 * 31)  # one month
def law_view(request, law_id, slug=None):
    law = get_object_or_404(models.Document, id=law_id)

    context = {'law': law, 'navigation_tab': 'documents'}

    return render(request, "law/document_view/main.html", context)


ANALYSIS_TITLES = {'law_count_time_series': _('How many laws are enacted yearly?'),
                   'law_eu_impact_time_series': _('Impact of EU Law in the Portuguese Law'),
                   'law_types_time_series': _('Evolution of the portuguese Law')}


def analysis_list(request):
    analysis_list = []
    analysis_dict = law.analysis.ANALYSIS

    for analysis in analysis_dict:
        analysis_list.append({
            'id': analysis_dict[analysis],
            'url': reverse('law_analysis_selector',
                           args=(analysis_dict[analysis],
                                 slugify(ANALYSIS_TITLES[analysis]))),
            'title': ANALYSIS_TITLES[analysis]
        })

    return render(request, "law/analysis.html", {'analysis': analysis_list, 'navigation_tab': 'analysis'})


def law_analysis(request, analysis_id, slug=None):
    try:
        analysis_id = int(analysis_id)
    except:
        raise Http404
    if int(analysis_id) not in law.analysis.PRIMARY_KEY:
        raise Http404

    name = law.analysis.PRIMARY_KEY[analysis_id]

    templates = {'law_count_time_series': 'law/analysis/laws_time_series.html',
                 'law_eu_impact_time_series': 'law/analysis/eu_impact.html',
                 'law_types_time_series': 'law/analysis/law_types_time_series/main.html'}

    if name not in templates:
        raise IndexError('Template for analysis "%s" not found' % name)

    context = {'title': ANALYSIS_TITLES[name], 'navigation_tab': 'analysis'}

    return render(request, templates[name], context)
