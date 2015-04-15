from __future__ import unicode_literals

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils import formats
from django.utils.translation import ugettext as _

from .models import Document, Type


class GeneralDocumentFeed(Feed):
    def item_title(self, item):
        return _('%(name)s - %(date)s - %(creator)s') % \
            {'name': item.name(),
             'date': formats.date_format(item.date),
             'creator': item.creator_name}

    def item_description(self, item):
        return item.summary

    def items(self, obj):
        return self._items(obj).order_by('-date', 'type__name', '-number') \
            .prefetch_related('type')[:200]

    def _items(self, obj):
        raise NotImplementedError


class LawsFeed(GeneralDocumentFeed):
    def title(self, __):
        return _("Série I of Diário da República")

    def link(self, _):
        return reverse('law_law_list')

    def description(self, __):
        return _("All documents published in Série I of Diário da República")

    def _items(self, _):
        return Document.objects.all()


class TypeDocumentsFeed(GeneralDocumentFeed):
    def get_object(self, request, type_id, slug=None):
        return get_object_or_404(Type, id=type_id)

    def title(self, obj):
        return obj.name

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return _("Documents") + "\"%s\"" % obj.name

    def _items(self, obj):
        return obj.document_set.all()


class DocumentFeed(GeneralDocumentFeed):

    def get_object(self, request, dre_doc_id, slug=None):
        return get_object_or_404(Document.objects.select_related('type'),
                                 dre_doc_id=dre_doc_id)

    def title(self, obj):
        return _("Laws referring %s") % obj.name()

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return _("All documents published in Série I of Diário da República "
                 "that refer %s") % obj.name()

    def _items(self, obj):
        return obj.document_set.all()
