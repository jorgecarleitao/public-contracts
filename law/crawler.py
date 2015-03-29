from main.tools import set_up
set_up.set_up_django_environment('main.settings')

import logging

from django.db import transaction

from law.crawler_forms import DocumentForm
from law.models import Document

logger = logging.getLogger(__name__)


def build_data(document, publication):
    """
    Maps the variables of pt_law_downloader to our form
    """
    return {'creator_name': publication['creator'],
            'type': publication['type'],
            'number': publication['number'],
            'text': publication['text'],
            'summary': publication['summary'],
            'date': publication['date'],

            'dre_doc_id': publication['dre_id'],
            'dre_pdf_id': publication['pdf_id'],
            'dr_pages': publication['pages'],
            'dr_series': document['series'],
            'dr_supplement': document['supplement'],
            'dr_number': document['number']
            }


# we want to ensure that the document is completely saved since pt_law_downloader
# uses documents as its atomic units.
@transaction.atomic
def save_document(document):
    for publication in document['publications']:
        # ignore publications without information.
        if publication['dre_id'] is None:
            continue

        form = DocumentForm(build_data(document, publication))

        if not form.is_valid():
            logger.error('Publication %d of doc %d failed.' %
                         (publication['dre_id'], document['dre_id']))
            raise ValueError('Data failed validation: %s' % form.errors)

        try:
            doc = Document.objects.get(dre_doc_id=form.cleaned_data['dre_doc_id'])
        except Document.DoesNotExist:
            doc = Document.objects.create(**form.cleaned_data)

        doc.update_references()
