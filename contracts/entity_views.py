from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum, Count, Q
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

import models
from views import build_contract_list_context


def main_view(request, entity_id, slug=None):
    entity = get_object_or_404(models.Entity, pk=entity_id)

    contracts = entity.last_contracts(5).prefetch_related("contracted", "contractors", "category")
    categories = models.Category.objects.filter(pk__in=list(contracts.values_list('category__id', flat=True)))

    context = {'entity': entity,
               'tab': 'summary',
               'last_contracts': contracts,
               'last_categories': categories}

    return render(request, 'contracts/entity_view/tab_data/main.html', context)


def contracts(request, entity_id):
    entity = get_object_or_404(models.Entity, pk=entity_id)

    all_contracts = entity.last_contracts().prefetch_related("contracted", "contractors", "category")

    context = {'entity': entity,
               'tab': 'contracts',
               'contracts': all_contracts}

    ## filter contracts by ordering and pagination
    context = build_contract_list_context(context, request.GET)

    return render(request, 'contracts/entity_view/tab_contracts/main.html', context)


def build_costumer_list_context(context, GET):
    ordering = {_('value'): 'value', _('name'): 'name', _('contracts'): 'contracts'}

    def apply_order(querySet, order):
        if order not in ordering:
            return querySet, False

        elif ordering[order] == 'value':
            return querySet.order_by('-total_expended'), True
        elif ordering[order] == 'name':
            return querySet.order_by('name'), True
        elif ordering[order] == 'contracts':
            return querySet.order_by('-total_contracts'), True

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
        if applied:
            context['sorting'] = ordering[order]

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


def costumers(request, entity_id):
    entity = get_object_or_404(models.Entity, pk=entity_id)

    all_costumers = models.Entity.objects.filter(contracts_made__contracted__id=entity_id).distinct()\
                   .annotate(total_expended=Sum("contracts_made__price"), total_contracts=Count("contracts_made__price"))

    context = {'entity': entity,
               'tab': 'costumers',
               'entities': all_costumers}

    ## filter entities by ordering and pagination
    context = build_costumer_list_context(context, request.GET)

    return render(request, 'contracts/entity_view/tab_costumers/main.html', context)
