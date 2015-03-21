import datetime
import json

from django.db import connection
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext as _

from . import models
from . import indexes
from .views import build_contract_list_context, build_tender_list_context,\
    build_entity_list_context
from .forms import CostumerSelectorForm
from .analysis.analysis import add_months


def main_view(request, entity_base_id, slug=None):
    entity = get_object_or_404(models.Entity.objects.select_related('data'),
                               base_id=entity_base_id)

    ids = entity.get_contracts_ids()
    contracts = models.Contract.objects.filter(id__in=ids['made'] + ids['set'])

    # optimization
    contracts = contracts.prefetch_related("contracted", "contractors")[:5]

    clients_hiring, hired_clients = entity.main_costumers()

    context = {'navigation_tab': 'entities',
               'entity': entity,
               'tab': 'summary',
               'contracts_made_count': len(ids['made']),
               'contracts_received_count': len(ids['set']),
               'last_contracts': contracts,
               'hired_clients': hired_clients,
               'clients_hiring': clients_hiring,
               'REQUIRE_D3JS': True}

    return render(request, 'contracts/entity_view/tab_data/main.html', context)


def contracts(request, entity_base_id):
    entity = get_object_or_404(models.Entity, base_id=entity_base_id)

    ids = entity.get_all_contracts_ids()
    contracts = indexes.ContractIndex.objects\
        .filter(id__in=ids)\
        .extra(select={'signing_date_is_null': 'signing_date IS NULL'},
               order_by=['signing_date_is_null', '-signing_date'])\
        .search_filter(id__in=ids)

    contracts = contracts.prefetch_related("contracted", "contractors")

    context = {'navigation_tab': 'entities',
               'entity': entity,
               'tab': 'contracts',
               'contracts': contracts,
               'REQUIRE_DATEPICKER': True}

    ## filter contracts by ordering and pagination
    context = build_contract_list_context(context, request.GET)

    return render(request, 'contracts/entity_view/tab_contracts/main.html', context)


def costumers(request, entity_base_id):
    entity = get_object_or_404(models.Entity, base_id=entity_base_id)

    all_costumers = indexes.EntityIndex.objects.all()\
        .filter(contracts_made__contracted__id=entity.id).distinct() \
        .annotate(total_expended=Sum("contracts_made__price"),
                  total_contracts=Count("contracts_made__price"))

    context = {'navigation_tab': 'entities',
               'entity': entity,
               'tab': 'costumers',
               'entities': all_costumers}

    # filter entities
    context = build_entity_list_context(context, request.GET,
                                        form_cls=CostumerSelectorForm)

    return render(request, 'contracts/entity_view/tab_costumers/main.html', context)


def tenders(request, entity_base_id):
    entity = get_object_or_404(models.Entity, base_id=entity_base_id)

    all_tenders = entity.tender_set.all()

    all_tenders = all_tenders.prefetch_related("contractors")

    context = {'navigation_tab': 'entities',
               'entity': entity,
               'tab': 'tenders',
               'tenders': all_tenders,
               'REQUIRE_DATEPICKER': True}

    ## filter entities by ordering and pagination
    context = build_tender_list_context(context, request.GET)

    return render(request, 'contracts/entity_view/tab_tenders/main.html', context)


def contracts_made_time_series(request, entity_base_id):
    """
    Computes the time series of number of contracts of entry with entity_id
    starting with startswith_string.
    """
    query = '''SELECT EXTRACT(YEAR FROM contracts_contract.signing_date) as s_year,
                  EXTRACT(MONTH FROM contracts_contract.signing_date) as s_month,
                  COUNT(contracts_contract.id)
                FROM contracts_contract
                     INNER JOIN contracts_contract_contractors
                         ON ( contracts_contract.id = contracts_contract_contractors.contract_id )
                     INNER JOIN contracts_entity
                         ON ( contracts_contract_contractors.entity_id = contracts_entity.id )
                WHERE contracts_entity.base_id = %s
                GROUP BY s_year, s_month
                ORDER BY s_year, s_month
                '''

    cursor = connection.cursor()
    cursor.execute(query, (entity_base_id,))

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


def contracts_received_time_series(request, entity_base_id):
    """
    Computes the time series of number of contracts of entry with entity_id
    starting with startswith_string.
    """
    query = '''SELECT EXTRACT(YEAR FROM contracts_contract.signing_date) as s_year,
                       EXTRACT(MONTH FROM contracts_contract.signing_date) as s_month,
                       COUNT(contracts_contract.id)
                FROM contracts_contract
                     INNER JOIN contracts_contract_contracted
                         ON ( contracts_contract.id = contracts_contract_contracted.contract_id )
                     INNER JOIN contracts_entity
                         ON ( contracts_contract_contracted.entity_id = contracts_entity.id )
                WHERE contracts_entity.base_id = %s
                GROUP BY s_year, s_month
                ORDER BY s_year, s_month
                '''

    cursor = connection.cursor()
    cursor.execute(query, (entity_base_id,))

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


def redirect_id(request, entity_id, url_ending=None):
    """
    Redirects a URL of an entity to its new url.
    """
    if url_ending is None:
        url_ending = ''

    entity = get_object_or_404(models.Entity.objects.using('old'), id=entity_id)

    return redirect(reverse('entity_id', args=(entity.base_id,)) + url_ending,
                    permanent=True)
