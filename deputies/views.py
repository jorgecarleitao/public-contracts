from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render
from django.db.models import Q, Count
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from . import models
from deputies.analysis import ANALYSIS, PRIMARY_KEY


def build_deputies_list_context(context, GET):
    def apply_order(querySet, order):
        ordering = {_('name'): 'name', _('mandates'): '-mandate_count'}

        if order not in ordering:
            return querySet, False

        return querySet.order_by(ordering[order]), True

    def filter_search(search):
        words = search.split(' ')
        _filter = Q()
        for word in words:
            _filter &= Q(name__icontains=word)
        return _filter

    key = _('search')
    if key in GET and GET[key]:
        search_Q = filter_search(GET[key])
        context[key] = GET[key]
        context['deputies'] = context['deputies'].filter(search_Q)
        context['search'] = GET[key]

    if _('sorting') in GET:
        order = GET[_('sorting')]

        context['deputies'], applied = apply_order(context['deputies'], order)

        # if it is a valid ordering, we send it to the template.
        order_name = {_('name'): 'name', _('mandates'): 'mandates'}
        if applied:
            context['ordering'] = order_name[order]

    paginator = Paginator(context['deputies'], 50)
    page = GET.get(_('page'))
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

    context = {'deputies': deputies}

    context = build_deputies_list_context(context, request.GET)

    return render(request, 'deputies/deputies_list.html', context)


def parties_list(request):

    parties = models.Party.objects.all()

    parties = parties.annotate(mandates_count=Count('mandate'), deputies_count=Count('mandate__deputy', distinct=True))

    return render(request, 'deputies/parties_list/main.html', {'parties': parties})


def party_view(request, party_id):

    party = models.Party.objects.get(id=party_id)
    deputies = models.Deputy.objects.filter(party_id=party_id)
    deputies = deputies.annotate(mandate_count=Count('mandate'))
    deputies = deputies.select_related("party__abbrev")

    party.deputies_count = models.Deputy.objects.filter(party_id=party_id).count()
    party.current_count = models.Deputy.objects.filter(party_id=party_id, is_active=True).count()

    party.mandates_count = party.mandate_set.count()

    context = {'party': party, 'deputies': deputies}

    context = build_deputies_list_context(context, request.GET)

    return render(request, 'deputies/party_view/main.html', context)


def legislatures(request):

    context = {'legislatures': models.Legislature.objects.all()}

    return render(request, 'deputies/legislatures_list.html', context)


ANALYSIS_TITLES = {}  #{'mandates_distribution': _('How many mandates a deputy is in the Parliament?')}


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

    templates = {}  #{'mandates_distribution': 'deputies/analysis/mandates_distribution.html'}

    if name not in templates:
        raise IndexError('Template for analysis "%s" not found' % name)

    context = {'title': ANALYSIS_TITLES[name], 'navigation_tab': 'analysis'}

    return render(request, templates[name], context)
