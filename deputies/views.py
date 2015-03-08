from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render
from django.db.models import Q, Count
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from . import models
from deputies.analysis import ANALYSIS, PRIMARY_KEY
from deputies.forms import DeputySelectorForm


def build_deputies_list_context(context, GET):
    """
    Uses parameters GET (from a request) to modify the context
    of deputies lists.

    Validates GET using ``DeputySelectorForm``, and uses the ``cleaned_data``
    to apply search and ordering to ``context['deputies']``.

    Returns the modified context.
    """
    page = GET.get(_('page'))

    context['selector'] = DeputySelectorForm(GET)
    if context['selector'].is_valid():
        GET = context['selector'].cleaned_data
    else:
        GET = {}

    def filter_search(search):
        words = search.split(' ')
        _filter = Q()
        for word in words:
            _filter &= Q(name__icontains=word)
        return _filter

    key = 'search'
    if key in GET and GET[key]:
        search_Q = filter_search(GET[key])
        context['deputies'] = context['deputies'].filter(search_Q)

    key = 'sorting'
    if key in GET and GET[key] in context['selector'].SORTING_LOOKUPS:
        context['deputies'] = context['deputies'].order_by(
            context['selector'].SORTING_LOOKUPS[GET[key]])

    paginator = Paginator(context['deputies'], 20)
    try:
        context['deputies'] = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        context['deputies'] = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        context['deputies'] = paginator.page(paginator.num_pages)

    return context


def home(request):
    return render(request, 'deputies/main_page.html')


def deputies_list(request):
    deputies = models.Deputy.objects.all()
    deputies = deputies.annotate(mandate_count=Count('mandate'))

    deputies = deputies.select_related("party__abbrev")

    context = {'deputies': deputies, 'navigation_tab': 'deputies'}

    context = build_deputies_list_context(context, request.GET)

    return render(request, 'deputies/deputies_list.html', context)


def parties_list(request):

    parties = models.Party.objects.all()

    parties = parties.annotate(mandates_count=Count('mandate'),
                               deputies_count=Count('mandate__deputy', distinct=True))

    return render(request, 'deputies/parties_list/main.html', {'parties': parties,
                                                               'navigation_tab': 'parties'})


def party_view(request, party_id):

    party = models.Party.objects.get(id=party_id)
    deputies = models.Deputy.objects.filter(party_id=party_id)
    deputies = deputies.annotate(mandate_count=Count('mandate'))
    deputies = deputies.select_related("party__abbrev")

    party.deputies_count = models.Deputy.objects.filter(party_id=party_id).count()
    party.current_count = models.Deputy.objects.filter(party_id=party_id, is_active=True).count()

    party.mandates_count = party.mandate_set.count()

    context = {'party': party,
               'deputies': deputies,
               'navigation_tab': 'parties'}

    context = build_deputies_list_context(context, request.GET)

    return render(request, 'deputies/party_view/main.html', context)


ANALYSIS_TITLES = {'mandates_distribution': _('How many mandates a deputy is in the Parliament?')}


def analysis_list(request):
    analysis_list = []
    analysis_dict = ANALYSIS

    for analysis in analysis_dict:
        if analysis in ANALYSIS_TITLES:
            analysis_list.append({
                'id': analysis_dict[analysis],
                'url': reverse('deputies_analysis_selector',
                               args=(analysis_dict[analysis],
                                     slugify(ANALYSIS_TITLES[analysis]))),
                'title': ANALYSIS_TITLES[analysis]
            })

    return render(request, "deputies/analysis.html", {'analysis': analysis_list, 'navigation_tab': 'analysis'})


def analysis(request, analysis_id, slug=None):
    try:
        analysis_id = int(analysis_id)
    except:
        raise Http404
    if analysis_id not in PRIMARY_KEY:
        raise Http404

    name = PRIMARY_KEY[analysis_id]

    templates = {'mandates_distribution': 'deputies/analysis/mandates_distribution.html'}

    if name not in templates:
        raise IndexError('Template for analysis "%s" not found' % name)

    context = {'title': ANALYSIS_TITLES[name], 'navigation_tab': 'analysis'}

    return render(request, templates[name], context)
