# coding=utf-8
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from main.domain import SITE_NAME

from .models import Category, Entity


class CategoryFeed(Feed):
    def get_object(self, request, category_id):
        return get_object_or_404(Category, id=category_id)

    def title(self, obj):
        return "%s - %s" % (SITE_NAME, obj.description_pt)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return _("Contracts in \"%s\"" % obj.description_pt)

    def item_title(self, item):
        price_str = u'unknown'
        if item.price:
            price_str = str(item.price/100)
        return price_str + u"€ - " + (item.contract_description or "no description")

    def item_description(self, item):
        result = "Contractors: "
        for x in item.contractors.all():
            result += x.name + "; "
        return result[:-2]

    def items(self, obj):
        return obj.contract_set.all()


class EntityFeed(Feed):
    def get_object(self, request, entity_id):
        return get_object_or_404(Entity, id=entity_id)

    def title(self, obj):
        return "%s - %s" % (SITE_NAME, obj.name)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return _("Contracts with \"%s\"" % obj.name)

    def item_title(self, item):
        price_str = u'unknown'
        if item.price:
            price_str = str(item.price/100)
        return price_str + u"€ - " + (item.contract_description or "no description")

    def item_description(self, item):
        result = "Contractors: "
        for x in item.contractors.all():
            result += x.name + "; "
        return result[:-2]

    def items(self, obj):
        return obj.contracts_made.all()
