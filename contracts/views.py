
from datetime import date
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.cache import cache_page
from django.db.models import Sum, Q
from django.utils.translation import ugettext as _
from django.shortcuts import render

from contracts import views_data
from contracts.analysis import get_time_difference
import models


def home(request):
    return render(request, 'contracts/main_page.html')


def build_contract_list_context(context, GET):
    def apply_order(querySet, order):
        ordering = {_('price'): '-price', _('date'): '-signing_date'}

        if order not in ordering:
            return querySet, False

        return querySet.order_by(ordering[order]), True

    def filter_search(search):
        words = search.split(' ')
        _filter = Q()
        for word in words:
            _filter &= Q(description__icontains=word)
        return _filter

    key = _('search')
    if key in GET and GET[key]:
        search_Q = filter_search(GET[key])
        context[key] = GET[key]
        context['contracts'] = context['contracts'].filter(search_Q)
        context['search'] = GET[key]

    if _('ordering') in GET:
        order = GET[_('ordering')]

        context['contracts'], applied = apply_order(context['contracts'], order)

        # if it is a valid ordering, we send it to the template.
        order_name = {_('price'): 'price', _('date'): 'date'}
        if applied:
            context['ordering'] = order_name[order]

    paginator = Paginator(context['contracts'], 20)
    page = GET.get(_('page'))
    try:
        context['contracts'] = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        context['contracts'] = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        context['contracts'] = paginator.page(paginator.num_pages)

    return context


#@cache_page(60 * 60 * 12)
def contracts_list(request):
    """
    View that controls the contracts list.
    """
    contracts = models.Contract.objects.all().order_by('-signing_date')
    context = {'contracts': contracts}

    context = build_contract_list_context(context, request.GET)

    today = date.today()
    contracts_year = contracts.filter(signing_date__year=today.year)
    contracts_month = contracts_year.filter(signing_date__month=today.month)

    context['total_price'] = contracts.aggregate(Sum('price'))['price__sum']
    context['year_price'] = contracts_year.aggregate(Sum('price'))['price__sum']
    context['month_price'] = contracts_month.aggregate(Sum('price'))['price__sum']

    return render(request, 'contracts/contracts_list.html', context)


def categories_list(request):
    """
    View that controls the categories list.
    """
    categories = models.Category.objects.filter(depth=1)
    context = {'categories': categories, 'contracts': models.Contract.objects.filter(cpvs='').order_by('-signing_date'),
               'no_code': True}

    context = build_contract_list_context(context, request.GET)

    return render(request, 'contracts/categories_list.html', context)


def category_view(request, category_id):
    """
    View that controls the view of a specific category.
    """
    category = models.Category.objects.get(pk=category_id)
    context = {'category': category, 'categories': category.get_children(),
               'contracts': category.own_contracts().order_by('-signing_date')}

    context = build_contract_list_context(context, request.GET)

    return render(request, 'contracts/categories_list.html', context)


def build_entity_list_context(context, GET):
    ordering = {_('earnings'): None, _('expenses'): None}

    def apply_order(querySet, order):
        if order not in ordering:
            return querySet, False

        if order == _('earnings'):
            return querySet.order_by('-data__total_earned'), True
        elif order == _('expenses'):
            return querySet.order_by('-data__total_expended'), True

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
        context['entities'] = context['entities'].filter(search_Q)
        context['search'] = GET[key]

    if _('ordering') in GET:
        order = GET[_('ordering')]

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
    entities = models.Entity.objects.all()

    context = {'entities': entities}

    context = build_entity_list_context(context, request.GET)

    return render(request, 'contracts/entities_list.html', context)


#@cache_page(60 * 60 * 24)
def entities_category_ranking(request):

    entities = views_data.get_entities_categories_ranking()
    count = 1
    for entity in entities:
        entity.rank = count
        count += 1

    paginator = Paginator(entities, 20)
    page = request.GET.get(_('page'))
    try:
        entities = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        entities = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        entities = paginator.page(paginator.num_pages)

    print entities.number

    context = {'entities': entities}

    return render(request, 'contracts/entity_rank.html', context)


def contracts_price_histogram(request):

    return render(request, 'contracts/contracts_price_histogram.html')
