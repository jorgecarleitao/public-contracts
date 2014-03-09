from datetime import date
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.shortcuts import render

import models


def about(request):
    return render(request, 'contracts/about.html')


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

    if _('sorting') in GET:
        order = GET[_('sorting')]

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


def contracts_list(request):
    """
    View that controls the contracts list.
    """
    contracts = models.Contract.objects.all().prefetch_related("contracted", "contractors", "category")
    context = {'contracts': contracts}

    context = build_contract_list_context(context, request.GET)

    today = date.today()
    contracts_year = contracts.filter(signing_date__year=today.year)
    contracts_month = contracts_year.filter(signing_date__month=today.month)

    return render(request, 'contracts/contract_list/main.html', context)


def categories_list(request):
    """
    View that controls the categories list.
    """
    categories = models.Category.objects.filter(depth=1)

    context = {'categories': categories,
               'contracts': models.Contract.objects.filter(category=None).prefetch_related("contracted", "contractors", "category"),
               'no_code': True}

    context = build_contract_list_context(context, request.GET)

    return render(request, 'contracts/category_list/main.html', context)


def category_view(request, category_id):
    """
    View that controls the view of a specific category.
    """
    category = models.Category.objects.get(pk=category_id)
    context = {'category': category,
               'categories': category.get_children(),
               'contracts': category.contract_set.all().prefetch_related("contracted", "contractors", "category")}

    context = build_contract_list_context(context, request.GET)

    return render(request, 'contracts/category_list/main.html', context)


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
    entities = models.Entity.objects.all().select_related("data")

    context = {'entities': entities}

    context = build_entity_list_context(context, request.GET)

    return render(request, 'contracts/entity_list/main.html', context)
