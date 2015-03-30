from django.shortcuts import render, get_object_or_404, redirect

from . import models


def main_view(request, contract_base_id):
    query = models.Contract.default_objects \
        .select_related('contract_type__name',
                        'category',
                        'country__name',
                        'district__name',
                        'council__name') \
        .prefetch_related('contractors', 'contracted')

    contract = get_object_or_404(query, base_id=contract_base_id)

    context = {'navigation_tab': 'contracts',
               'contract': contract}

    return render(request, 'contracts/contract_view/main.html', context)


def redirect_id(request, contract_id):
    """
    Returns the contract
    """
    contract = get_object_or_404(models.Contract.objects.using('old'),
                                 id=contract_id)

    return redirect(contract, permanent=True)
