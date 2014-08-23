from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect

from . import models
from contracts.analysis import add_months
from contracts.forms import ContractSelectorForm, TenderSelectorForm

from . import indexes
from contracts.views_analysis import analysis_list


def home(request):

    today = now().date()
    last_month = add_months(today, -1)

    latest_contracts = models.Contract.objects.filter(
        signing_date__gt=last_month).order_by('-price')[:5]

    latest_entities = models.Entity.objects.order_by('-id')[:5]

    latest_tenders = models.Tender.objects.order_by('-id')[:5]

    latest_analysis = analysis_list()[-5:]

    return render(request, 'contracts/main_page.html', {
        'latest_contracts': latest_contracts,
        'latest_entities': latest_entities,
        'latest_tenders': latest_tenders,
        'latest_analysis': latest_analysis})


def build_contract_list_context(context, GET):
    """
    Uses parameters GET (from a request) to modify the context
    of contracts lists.

    Validates GET using ``ContractSelectorForm``, and uses
    the ``cleaned_data`` to apply date filter, search,
    and ordering to ``context['contracts']``.

    Returns the modified context.
    """
    page = GET.get(_('page'))

    context['selector'] = ContractSelectorForm(GET)
    if context['selector'].is_valid():
        GET = context['selector'].cleaned_data
    else:
        GET = {}

    key = 'search'
    if key in GET and GET[key]:
        context[key] = GET[key]
        context['contracts'] = context['contracts'].search(GET[key])

    key = 'range'
    if key in GET and GET[key]:
        start_date = GET[key][0]
        end_date = GET[key][1]
        if context['contracts'].search_mode:
            context['contracts'] = context['contracts'].search_filter(signing_date__gte=start_date,
                                                                      signing_date__lte=end_date)
        else:
            context['contracts'] = context['contracts'].filter(signing_date__gte=start_date,
                                                               signing_date__lte=end_date)

    key = 'sorting'
    if key in GET and GET[key] in context['selector'].SORTING_LOOKUPS:
        context['contracts'] = context['contracts'].order_by(
            context['selector'].SORTING_LOOKUPS[GET[key]])

    paginator = Paginator(context['contracts'], 20)
    try:
        context['contracts'] = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        context['contracts'] = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        context['contracts'] = paginator.page(paginator.num_pages)

    return context


def contracts_list(request):
    """
    View that controls the contracts list.
    """
    contracts = indexes.ContractIndex.objects.all().prefetch_related("contracted", "contractors", "category")
    context = {'contracts': contracts, 'navigation_tab': 'contracts'}

    context = build_contract_list_context(context, request.GET)

    return render(request, 'contracts/contract_list/main.html', context)


def categories_list(request):
    """
    View that controls the categories list.
    """
    categories = models.Category.objects.filter(depth=1)

    context = {'navigation_tab': 'categories',
               'categories': categories,
               'no_code': True,
               }

    return render(request, 'contracts/category_list/main.html', context)


def build_entity_list_context(context, GET):
    ordering = {_('earnings'): None, _('expenses'): None}

    def apply_order(querySet, order):
        if order not in ordering:
            return querySet, False

        if order == _('earnings'):
            return querySet.order_by('-data__total_earned').search_order_by(), True
        elif order == _('expenses'):
            return querySet.order_by('-data__total_expended').search_order_by(), True

    key = _('search')
    if key in GET and GET[key]:
        context[key] = GET[key]

        try:
            nif = int(GET[key])
            context['entities'] = context['entities'].filter(nif__contains=nif)
        except ValueError:
            nif = None
        if not nif:
            context['entities'] = context['entities'].search(GET[key])

        context['search'] = GET[key]

    if _('sorting') in GET:
        order = GET[_('sorting')]

        context['entities'], applied = apply_order(context['entities'], order)

        # if it is a valid ordering, we send it to the template.
        order_name = {_('earnings'): 'earnings', _('expenses'): 'expenses'}
        if applied:
            context['ordering'] = order_name[order]

    paginator = Paginator(context['entities'], 20)
    page = GET.get(_('page'))
    try:
        context['entities'] = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        context['entities'] = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        context['entities'] = paginator.page(paginator.num_pages)

    return context


def entities_list(request):
    entities = indexes.EntityIndex.objects.all().select_related("data")

    context = {'navigation_tab': 'entities',
               'entities': entities}

    context = build_entity_list_context(context, request.GET)

    # if we find only one, we redirect.
    if len(context['entities']) == 1:
        return redirect(context['entities'][0].get_absolute_url())

    return render(request, 'contracts/entity_list/main.html', context)


def build_tender_list_context(context, GET):
    page = GET.get(_('page'))

    context['selector'] = TenderSelectorForm(GET)
    if context['selector'].is_valid():
        GET = context['selector'].cleaned_data
    else:
        GET = {}

    key = 'search'
    if key in GET and GET[key]:
        context[key] = GET[key]
        context['tenders'] = context['tenders'].filter(description__search=GET[key])

    key = 'range'
    if key in GET and GET[key]:
        start_date = GET[key][0]
        end_date = GET[key][1]
        context['tenders'] = context['tenders'].filter(
            publication_date__gte=start_date,
            publication_date__lte=end_date)

    key = 'sorting'
    if key in GET and GET[key] in context['selector'].SORTING_LOOKUPS:
        context['tenders'] = context['tenders'].order_by(
            context['selector'].SORTING_LOOKUPS[GET[key]])

    paginator = Paginator(context['tenders'], 20)
    try:
        context['tenders'] = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        context['tenders'] = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        context['tenders'] = paginator.page(paginator.num_pages)

    return context


def tenders_list(request):
    tenders = models.Tender.objects.all().prefetch_related('contractors')

    context = {'navigation_tab': 'tenders',
               'tenders': tenders}

    context = build_tender_list_context(context, request.GET)

    return render(request, 'contracts/tender_list/main.html', context)
