from django.shortcuts import render, get_object_or_404

from . import models


def main_view(request, contract_id):
    query = models.Contract.objects.select_related('contract_type__name',
                                                   'category__id',
                                                   'category__name',
                                                   'country__name',
                                                   'district__name',
                                                   'council__name')

    contract = get_object_or_404(query, pk=contract_id)

    context = {'navigation_tab': 'contracts',
               'contract': contract}

    return render(request, 'contracts/contract_view/main.html', context)
