import datetime
import json

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import connection
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from . import models
from . import indexes
from .views import build_contract_list_context, build_tender_list_context
from .analysis.analysis import add_months


def main_view(request, entity_id, slug=None):
    entity = get_object_or_404(models.Entity.objects.select_related('data'),
                               pk=entity_id)

    ids = entity.get_contracts_ids()
    contracts = models.Contract.objects.filter(id__in=ids['made'] + ids['set'])

    # optimization
    contracts = contracts.prefetch_related("contracted", "contractors")[:5]

    categories = models.Category.objects.filter(pk__in=[c.category_id
                                                        for c in contracts])
    clients_hiring, hired_clients = entity.main_costumers()

    context = {'navigation_tab': 'entities',
               'entity': entity,
               'tab': 'summary',
               'contracts_made_count': len(ids['made']),
               'contracts_received_count': len(ids['set']),
               'last_contracts': contracts,
               'last_categories': categories,
               'hired_clients': hired_clients,
               'clients_hiring': clients_hiring}

    return render(request, 'contracts/entity_view/tab_data/main.html', context)


def contracts(request, entity_id):
    entity = get_object_or_404(models.Entity, pk=entity_id)

    contracts = indexes.ContractIndex.objects\
        .filter(id__in=entity.get_all_contracts_ids())\
        .search_filter(id__in=entity.get_all_contracts_ids())

    contracts = contracts.prefetch_related("contracted", "contractors")

    context = {'navigation_tab': 'entities',
               'entity': entity,
               'tab': 'contracts',
               'contracts': contracts}

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

    key = _('search')
    if key in GET and GET[key]:
        context[key] = GET[key]

        try:
            nif = int(GET[key])
            context['entities'] = context['entities'].filter(nif__contains=nif)
        except ValueError:
            nif = None
        if not nif:
            context['entities'] = context['entities'].filter(name__search=GET[key])

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

    all_costumers = models.Entity.objects.filter(contracts_made__contracted__id=entity_id).distinct() \
        .annotate(total_expended=Sum("contracts_made__price"), total_contracts=Count("contracts_made__price"))

    context = {'navigation_tab': 'entities',
               'entity': entity,
               'tab': 'costumers',
               'entities': all_costumers}

    ## filter entities by ordering and pagination
    context = build_costumer_list_context(context, request.GET)

    return render(request, 'contracts/entity_view/tab_costumers/main.html', context)


def tenders(request, entity_id):
    entity = get_object_or_404(models.Entity, pk=entity_id)

    all_tenders = entity.tender_set.all()

    context = {'navigation_tab': 'entities',
               'entity': entity,
               'tab': 'tenders',
               'tenders': all_tenders}

    ## filter entities by ordering and pagination
    context = build_tender_list_context(context, request.GET)

    return render(request, 'contracts/entity_view/tab_tenders/main.html', context)


def contracts_made_time_series(request, entity_id):
    """
    Computes the time series of number of contracts of entry with entity_id
    starting with startswith_string.
    """
    query = '''SELECT YEAR(`contracts_contract`.`signing_date`),
                       MONTH(`contracts_contract`.`signing_date`),
                       COUNT(`contracts_contract`.`id`)
                FROM `contracts_contract`
                     INNER JOIN `contracts_contract_contractors`
                         ON ( `contracts_contract`.`id` = `contracts_contract_contractors`.`contract_id` )
                     INNER JOIN `contracts_entity`
                         ON ( `contracts_contract_contractors`.`entity_id` = `contracts_entity`.`id` )
                WHERE `contracts_entity`.`id` = %s
                GROUP BY YEAR(`contracts_contract`.`signing_date`), MONTH(`contracts_contract`.`signing_date`)
                '''

    cursor = connection.cursor()
    cursor.execute(query, entity_id)

    data = {'values': [], 'key': _('Contracts as hiring')}
    for row in cursor.fetchall():
        year, month, value = row
        if year is None:
            continue

        min_date = datetime.date(int(year), int(month), 1)
        max_date = add_months(min_date, 1)

        entry = {'month': min_date.strftime('%Y-%m'),
                 'value': int(value)}
        data['values'].append(entry)

    return HttpResponse(json.dumps([data]), content_type="application/json")


def contracts_received_time_series(request, entity_id):
    """
    Computes the time series of number of contracts of entry with entity_id
    starting with startswith_string.
    """
    query = '''SELECT YEAR(`contracts_contract`.`signing_date`),
                       MONTH(`contracts_contract`.`signing_date`),
                       COUNT(`contracts_contract`.`id`)
                FROM `contracts_contract`
                     INNER JOIN `contracts_contract_contracted`
                         ON ( `contracts_contract`.`id` = `contracts_contract_contracted`.`contract_id` )
                     INNER JOIN `contracts_entity`
                         ON ( `contracts_contract_contracted`.`entity_id` = `contracts_entity`.`id` )
                WHERE `contracts_entity`.`id` = %s
                GROUP BY YEAR(`contracts_contract`.`signing_date`), MONTH(`contracts_contract`.`signing_date`)
                '''

    cursor = connection.cursor()
    cursor.execute(query, entity_id)

    data = {'values': [], 'key': _('Contracts as hired')}
    for row in cursor.fetchall():
        year, month, value = row
        if year is None:
            continue

        min_date = datetime.date(int(year), int(month), 1)

        entry = {'month': min_date.strftime('%Y-%m'),
                 'value': int(value)}
        data['values'].append(entry)

    return HttpResponse(json.dumps([data]), content_type="application/json")
