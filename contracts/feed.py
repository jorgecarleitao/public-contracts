# coding=utf-8
from __future__ import unicode_literals

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from main.domain import SITE_NAME

from .models import Category, Entity, Contract, Tender


class CategoryContractsFeed(Feed):
    def get_object(self, request, category_id):
        return get_object_or_404(Category, id=category_id)

    def title(self, obj):
        return "%s - %s" % (SITE_NAME, obj.description_pt)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return _("Contracts in \"%s\"" % obj.description_pt)

    def item_title(self, item):
        price_str = 'unknown'
        if item.price:
            price_str = str(item.price/100)
        return price_str + "€ - " + (item.contract_description or "no description")

    def item_description(self, item):
        result = "Contractors: "
        for x in item.contractors.all():
            result += x.name + "; "
        return result[:-2]

    def items(self, obj):
        return obj.contract_set.all()


class CategoryTendersFeed(CategoryContractsFeed):
    def description(self, obj):
        return _("Tenders in \"%s\"" % obj.description_pt)

    def item_title(self, item):
        price_str = 'unknown'
        if item.price:
            price_str = str(item.price/100)
        return price_str + "€ - DEADLINE: " + item.deadline_date.strftime("%Y-%m-%d") +\
               " - " + (item.description or "no description")

    def item_description(self, item):
        result = "Contractors: "
        for x in item.contractors.all():
            result += x.name + "; "
        return result[:-2]

    def item_link(self, item):
        return item.get_dre_url()

    def items(self, _):
        return Tender.objects.all()[:200]


class ContractsFeed(Feed):
    def title(self, _):
        return "Contracts in %s" % SITE_NAME

    def link(self, _):
        return reverse('contracts_list_feed')

    def description(self, __):
        return _("Latest contracts in %s" % SITE_NAME)

    def item_title(self, item):
        price_str = 'unknown'
        if item.price:
            price_str = str(item.price/100)
        return price_str + "€ - " + (item.contract_description or "no description")

    def item_description(self, item):
        result = "Contractors: "
        for x in item.contractors.all():
            result += x.name + "; "
        return result[:-2]

    def items(self, _):
        return Contract.objects.all()[:200]


class EntityContractsFeed(Feed):
    def get_object(self, request, entity_id):
        return get_object_or_404(Entity, id=entity_id)

    def title(self, obj):
        return "%s - %s" % (SITE_NAME, obj.name)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return _("Contracts with \"%s\"" % obj.name)

    def item_title(self, item):
        price_str = 'unknown'
        if item.price:
            price_str = str(item.price/100)
        return price_str + "€ - " + (item.contract_description or "no description")

    def item_description(self, item):
        result = "Contractors: "
        for x in item.contractors.all():
            result += x.name + "; "
        return result[:-2]

    def items(self, obj):
        return obj.last_contracts()


class EntityTendersFeed(EntityContractsFeed):
    def description(self, obj):
        return _("Tenders created by \"%s\"" % obj.name)

    def item_title(self, item):
        price_str = 'unknown'
        if item.price:
            price_str = str(item.price/100)
        return price_str + "€ - DEADLINE: " + item.deadline_date.strftime("%Y-%m-%d") +\
               " - " + (item.description or "no description")

    def item_description(self, item):
        result = "Contractors: "
        for x in item.contractors.all():
            result += x.name + "; "
        return result[:-2]

    def item_link(self, item):
        return item.get_dre_url()

    def items(self, _):
        return Tender.objects.all()[:200]


class TendersFeed(Feed):
    def title(self, _):
        return "Tenders in %s" % SITE_NAME

    def link(self, _):
        return reverse('tenders_list_feed')

    def description(self, __):
        return _("Latest tenders in %s" % SITE_NAME)

    def item_title(self, item):
        price_str = 'unknown'
        if item.price:
            price_str = str(item.price/100)
        return price_str + "€ - DEADLINE: " + item.deadline_date.strftime("%Y-%m-%d") +\
               " - " + (item.description or "no description")

    def item_link(self, item):
        return item.get_dre_url()

    def item_description(self, item):
        result = "Contractors: "
        for x in item.contractors.all():
            result += x.name + "; "
        return result[:-2]

    def items(self, _):
        return Tender.objects.all()[:200]
