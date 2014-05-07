from django.shortcuts import render, get_object_or_404

from . import models


def main_view(request, contract_id):
    contract = get_object_or_404(models.Contract, pk=contract_id)

    context = {'navigation_tab': 'contracts',
               'contract': contract}

    return render(request, 'contracts/contract_view/main.html', context)
