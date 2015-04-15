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
                                  item.creator_name)

    def item_description(self, item):
        return item.summary

    def items(self, _):
        return Document.objects.order_by('-date')\
            .prefetch_related('type')[:200]


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
                                  item.creator_name)

    def item_description(self, item):
        return item.summary

    def items(self, obj):
        return obj.document_set.order_by('-date')\
            .prefetch_related('type')[:200]


class DocumentFeed(Feed):

    def get_object(self, request, dre_doc_id, slug=None):
        return get_object_or_404(Document.objects.select_related('type'),
                                 dre_doc_id=dre_doc_id)

    def title(self, obj):
        return _("Laws refering %s") % obj.name()

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return _("Documents from Series I of Diário da República that refer to %s")\
               % obj.name()

    def item_title(self, item):
        return _('%(name)s of %(date)s - %(creator)s') % \
               {'name': item.name(),
                'date': formats.date_format(item.date),
                'creator': item.creator_name}

    def item_description(self, item):
        return item.summary

    def items(self, obj):
        return obj.document_set.all()\
            .order_by('-date', 'type__name', '-number').select_related('type')
