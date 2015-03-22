from django.test import TestCase

from law.crawler_forms import DocumentForm
from law.models import Type


class TestCrawler(TestCase):

    def test_form(self):
        data = {'type': 'Portaria',
                'number': '1/2000',
                'creator_name': 'Min',
                'date': '2013-02-01',
                'summary': 'adda',
                'text': 'text',
                'dre_doc_id': 2,
                'dre_pdf_id': 2,
                'dr_series': 'I',
                'dr_number': '3',
                'dr_supplement': None,
                'dr_pages': '1-2'
        }

        DocumentForm(data)
        form = DocumentForm(data)

        self.assertTrue(form.is_valid())

        self.assertEqual(Type.objects.count(), 1)

        self.assertEqual(Type.objects.filter(name='Portaria', dr_series='I').count(), 1)
