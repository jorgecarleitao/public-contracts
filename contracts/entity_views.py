from django.shortcuts import render, get_object_or_404

import models
from views import build_contract_list_context


def main_view(request, entity_id, slug=None):
    entity = get_object_or_404(models.Entity, pk=entity_id)

    categories = []
    contracts = entity.last_contracts(5)

    for contract in contracts:
        if contract.category:
            categories.append(contract.category)

    context = {'entity': entity,
               'tab': 'summary',
               'last_contracts': contracts,
               'last_categories': categories}

    return render(request, 'contracts/entity_view/tab_data/main.html', context)


def contracts(request, entity_id):
    entity = get_object_or_404(models.Entity, pk=entity_id)

    all_contracts = entity.contracts_made.order_by('-signing_date')

    context = {'entity': entity,
               'tab': 'contracts',
               'contracts': all_contracts}

    ## filter contracts by ordering and pagination
    context = build_contract_list_context(context, request.GET)

    return render(request, 'contracts/entity_view/tab_contracts/main.html', context)
