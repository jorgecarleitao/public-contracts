from django.db.models import Sum, Count
from django.shortcuts import render, get_object_or_404

from . import indexes
from . import models
from .views import build_contract_list_context, build_tender_list_context
from .entity_views import build_costumer_list_context


def main_view(request, category_id):
    category = get_object_or_404(models.Category, pk=category_id)
    categories_ids = list(models.Category.get_tree(category).values_list('id'))

    context = {'navigation_tab': 'categories',
               'category': category,
               'categories': category.get_children(),
               'tab': 'summary'}

    context['contract_count'] = category.contracts_count()
    context['contract_price'] = category.contracts_price()

    context['contractors_count'] = models.Entity.objects.filter(contracts_made__category_id__in=categories_ids).distinct().count()
    context['contracted_count'] = models.Entity.objects.filter(contract__category_id__in=categories_ids).distinct().count()

    return render(request, 'contracts/category_view/tab_summary/main.html', context)


def contracts(request, category_id):
    category = get_object_or_404(models.Category, pk=category_id)
    categories_ids = models.Category.get_tree(category).values_list('id', flat=True)

    contracts = indexes.ContractIndex.objects.filter(category_id__in=categories_ids)\
        .search_filter(category_id__in=list(categories_ids))\
        .prefetch_related("contracted", "contractors", "category")

    context = {'navigation_tab': 'categories',
               'category': category,
               'tab': 'contracts',
               'contracts': contracts}

    ## filter contracts by ordering and pagination
    context = build_contract_list_context(context, request.GET)

    return render(request, 'contracts/category_view/tab_contracts/main.html', context)


def contractors(request, category_id):
    category = get_object_or_404(models.Category, pk=category_id)
    categories_ids = list(models.Category.get_tree(category).values_list('id'))

    entities = models.Entity.objects.filter(contracts_made__category_id__in=categories_ids).distinct()\
               .annotate(total_expended=Sum("contracts_made__price"), total_contracts=Count("contracts_made__price"))

    context = {'navigation_tab': 'categories',
               'category': category,
               'tab': 'contractors',
               'entities': entities}

    ## filter entities by ordering and pagination
    context = build_costumer_list_context(context, request.GET)

    return render(request, 'contracts/category_view/tab_entities/main.html', context)


def contracted(request, category_id):
    category = get_object_or_404(models.Category, pk=category_id)
    categories_ids = list(models.Category.get_tree(category).values_list('id'))

    entities = models.Entity.objects.filter(contract__category_id__in=categories_ids).distinct()\
               .annotate(total_expended=Sum("contract__price"), total_contracts=Count("contract__price"))

    context = {'navigation_tab': 'categories',
               'category': category,
               'tab': 'contracted',
               'entities': entities}

    ## filter entities by ordering and pagination
    context = build_costumer_list_context(context, request.GET)

    return render(request, 'contracts/category_view/tab_entities/main.html', context)


def tenders(request, category_id):
    category = get_object_or_404(models.Category, pk=category_id)
    categories_ids = list(models.Category.get_tree(category).values_list('id'))

    tenders = models.Tender.objects.filter(category_id__in=categories_ids)

    context = {'navigation_tab': 'categories',
               'category': category,
               'tab': 'tenders',
               'tenders': tenders}

    ## filter entities by ordering and pagination
    context = build_tender_list_context(context, request.GET)

    return render(request, 'contracts/category_view/tab_tenders/main.html', context)
