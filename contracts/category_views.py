from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum, Count, Q
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

import models
from views import build_contract_list_context, build_tender_list_context, build_entity_list_context


def main_view(request, category_id):
    category = get_object_or_404(models.Category, pk=category_id)

    context = {'category': category,
               'categories': category.get_children(),
               'tab': 'summary'}

    result = category.contract_set.aggregate(count=Count('id'), price=Sum('price'))
    context['contract_count'] = result['count']
    context['contract_price'] = result['price']

    context['contractors_count'] = models.Entity.objects.filter(contracts_made__category__id=category_id).distinct().count()
    context['contracted_count'] = models.Entity.objects.filter(contract__category__id=category_id).distinct().count()

    return render(request, 'contracts/category_view/tab_summary/main.html', context)


def contracts(request, category_id):
    category = get_object_or_404(models.Category, pk=category_id)

    contracts = category.contract_set.all().prefetch_related("contracted", "contractors", "category")

    context = {'category': category,
               'tab': 'contracts',
               'contracts': contracts}

    ## filter contracts by ordering and pagination
    context = build_contract_list_context(context, request.GET)

    return render(request, 'contracts/category_view/tab_contracts/main.html', context)


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


def contractors(request, category_id):
    category = get_object_or_404(models.Category, pk=category_id)

    entities = models.Entity.objects.filter(contracts_made__category__id=category_id).distinct()\
               .annotate(total_expended=Sum("contracts_made__price"), total_contracts=Count("contracts_made__price"))

    context = {'category': category,
               'tab': 'contractors',
               'entities': entities}

    ## filter entities by ordering and pagination
    context = build_costumer_list_context(context, request.GET)

    return render(request, 'contracts/category_view/tab_entities/main.html', context)


def contracted(request, category_id):
    category = get_object_or_404(models.Category, pk=category_id)

    entities = models.Entity.objects.filter(contract__category__id=category_id).distinct()\
               .annotate(total_expended=Sum("contract__price"), total_contracts=Count("contract__price"))

    context = {'category': category,
               'tab': 'contracted',
               'entities': entities}

    ## filter entities by ordering and pagination
    context = build_costumer_list_context(context, request.GET)

    return render(request, 'contracts/category_view/tab_entities/main.html', context)



def tenders(request, entity_id):
    entity = get_object_or_404(models.Entity, pk=entity_id)

    all_tenders = entity.tender_set.all()

    context = {'entity': entity,
               'tab': 'tenders',
               'tenders': all_tenders}

    ## filter entities by ordering and pagination
    context = build_tender_list_context(context, request.GET)

    return render(request, 'contracts/entity_view/tab_tenders/main.html', context)
