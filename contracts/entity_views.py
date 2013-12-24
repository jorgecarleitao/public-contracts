from django.shortcuts import render, get_object_or_404

import models


def main_view(request, entity_id):
    entity = get_object_or_404(models.Entity, pk=entity_id)

    if 'tab' in request.GET:
        return tab_data(request, entity)
    else:
        return tab_data(request, entity)


def tab_data(request, entity):

    categories = []
    contracts = entity.last_contracts(5)

    for contract in contracts:
        if contract.category:
            categories.append(contract.category)

    context = {'entity': entity,
               'tab': 'data',
               'last_contracts': contracts,
               'last_categories': categories}

    return render(request, 'contracts/entity_view/tab_data/main.html', context)
