from django.test import TestCase

from pt_law_downloader import get_publication, get_document
from law.crawler import save_publication, save_document
from law.crawler_forms import DocumentForm
from law.models import Type, Document


class TestCrawler(TestCase):

    def test_form(self):
        """
        Notice that `type` slightly changes, since we map it to the corrent term.
        """
        data = {'type': 'Declaração de Rectificação',
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

        self.assertEqual(1, Type.objects.count())

        self.assertEqual(1, Type.objects.filter(name='Declaração de Retificação',
                                                dr_series='I').count())

    def test_valid_insertion(self):
        pub1 = get_publication(544590)
        pub2 = get_publication(67040491)
        doc = {'series': 'I', 'supplement': None, 'number': '1/2000', 'dre_id': 1}
        save_publication(pub1, doc)
        save_publication(pub2, doc)
        self.assertEqual(2, Document.objects.count())
        self.assertEqual(1, Type.objects.filter(name='Portaria', dr_series='I').count())

        pub = Document.objects.get(dre_doc_id=67040491)

        self.assertEqual(1, pub.references.count())

    def test_invalid_insertion(self):
        pub = get_publication(544590)
        doc = {'series': 'I'*30, 'supplement': None, 'number': '1', 'dre_id': 1}
        with self.assertRaises(ValueError):
            save_publication(pub, doc)

    def test_638275(self):
        """
        This is an edge case, thus we test it explicitly.
        """
        pub = get_publication(638275)
        doc = {'series': 'I', 'supplement': None, 'number': '1', 'dre_id': 1}
        save_publication(pub, doc)

        pub = Document.objects.get(dre_doc_id=638275)

        self.assertEqual('4/93', pub.number)

    def test_save_doc(self):
        save_document(get_document(67142145))

    def test_empty_doc(self):
        """
        Test that empty publications are ignored.
        """
        doc = {'publications': [{'dre_id': None}, {'dre_id': None}]}
        save_document(doc)
        self.assertEqual(0, Type.objects.count())
        self.assertEqual(0, Document.objects.count())
