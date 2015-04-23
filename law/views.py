import re

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page

from . import models
from . import indexes
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
        # try a match on the law by <type_name> <number>
        match = re.search(r'^(.+?(?=([^\s]+\/\d{2,4}(\/[A-Z])?)))', GET[key])
        if match:
            type_name, number = match.group(1).strip(), match.group(2)
            context['laws'] = context['laws'].filter(number=number,
                                                     type__name__icontains=type_name)
        else:
            context['laws'] = context['laws'].search(GET[key])

    key = 'range'
    if key in GET and GET[key]:
        start_date = GET[key][0]
        end_date = GET[key][1]
        context['laws'] = context['laws'].filter(date__gte=start_date,
                                                 date__lte=end_date)

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
    return render(request, "law/home.html", {'REQUIRE_D3JS': True})


@cache_page(60 * 60 * 24)
def law_list(request):
    context = {'laws': indexes.DocumentIndex.objects
                             .order_by("-dre_doc_id")
                             .prefetch_related("type"),
               'navigation_tab': 'documents',
               'REQUIRE_DATEPICKER': True,
               }

    context = build_laws_list_context(context, request.GET)

    return render(request, "law/law_list/main.html", context)


@cache_page(60 * 60 * 24)
def types_list(request):
    types = models.Type.objects.filter(dr_series='I')\
        .annotate(count=Count('document')).order_by('-count', 'name')

    context = {'types': types, 'navigation_tab': 'types'}

    return render(request, "law/type_list/main.html", context)


def type_view(request, type_id, slug=None):
    type = get_object_or_404(models.Type, id=type_id)

    context = {'type': type,
               'laws': type.document_set.order_by("-date").prefetch_related("type"),
               'navigation_tab': 'types'}

    context = build_laws_list_context(context, request.GET)

    return render(request, "law/type_view/main.html", context)


def law_view(request, dre_doc_id, slug=None):
    law = get_object_or_404(models.Document.objects.select_related('type'),
                            dre_doc_id=dre_doc_id)

    related = law.document_set.all().order_by('-date', 'type__name',
                                              '-number').select_related('type')
    references = law.references.all().order_by('-date', 'type__name',
                                               '-number').select_related('type')

    context = {'law': law, 'navigation_tab': 'documents', 'related': related,
               'references': references}

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

    context = {'title': ANALYSIS_TITLES[name], 'navigation_tab': 'analysis',
               'REQUIRE_D3JS': True}

    return render(request, templates[name], context)


def redirect_id(request, document_id, url_ending=None):
    """
    Redirects an URL of a document to its new url.
    """
    old_document = get_object_or_404(models.Document.objects.using('old')
                                     .select_related('type__name')
                                     .values_list('type__name', 'date', 'number')
                                     , id=document_id)

    try:
        document = models.Document.objects.exclude(dr_series='II') \
            .get(type__name=old_document[0], date=old_document[1],
                 number=old_document[2])

    except models.Document.DoesNotExist:
        raise Http404

    return redirect(document, permanent=True)
