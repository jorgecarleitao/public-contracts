from __future__ import unicode_literals

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils import formats
from django.utils.translation import ugettext as _

from main.domain import SITE_NAME

from .models import Document, Type


class LawsFeed(Feed):
    def title(self, __):
        return _("Laws in %s" % SITE_NAME)

    def link(self, _):
        return reverse('laws_list_feed')

    def description(self, __):
        return _("Latest laws in %s" % SITE_NAME)

    def item_title(self, item):
        return '%s of %s - %s' % (item.name(),
                                  formats.date_format(item.date),
                                  item.creator.name)

    def item_description(self, item):
        return item.summary

    def items(self, _):
        return Document.laws.order_by('-date')\
            .prefetch_related('type', 'creator')[:200]


class TypeDocumentsFeed(Feed):
    def get_object(self, request, type_id, slug=None):
        return get_object_or_404(Type, id=type_id)

    def title(self, obj):
        return "%s in %s" % (obj.name, SITE_NAME)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return _("Documents") + "\"%s\"" % obj.name

    def item_title(self, item):
        return '%s of %s - %s' % (item.name(),
                                  formats.date_format(item.date),
                                  item.creator.name)

    def item_description(self, item):
        return item.summary

    def items(self, obj):
        return obj.document_set.order_by('-date')\
            .prefetch_related('type', 'creator')[:200]
