import unittest

from django.test import TestCase
from django.core.urlresolvers import reverse

from pt_law_downloader import get_publication

from law.crawler import save_publication
from law.models import Type, Document

from law.views import home, law_list, types_list, law_view, type_view, \
    analysis_list, build_laws_list_context, law_analysis
from law.views_data import analysis_selector


def _add_document(pub_id):
        pub = get_publication(pub_id)
        doc = {'series': 'I', 'supplement': None, 'number': '1', 'dre_id': 1}
        save_publication(pub, doc)


class TestBasic(TestCase):
    def test_home(self):
        response = self.client.get(reverse(home))
        self.assertEqual(200, response.status_code)

    def test_types_list(self):
        response = self.client.get(reverse(types_list))
        self.assertEqual(200, response.status_code)
        self.assertEqual('types', response.context['navigation_tab'])

    def test_law_and_type_view(self):
        # law_view
        response = self.client.get(reverse(law_view, args=(638275,)))
        self.assertEqual(404, response.status_code)

        # type_view
        response = self.client.get(reverse(type_view, args=(1,)))
        self.assertEqual(404, response.status_code)

        _add_document(638275)

        # law_view
        response = self.client.get(reverse(law_view, args=(638275,)))
        self.assertEqual(200, response.status_code)

        # type_view
        type = Type.objects.get()
        response = self.client.get(reverse(type_view, args=(type.id,)))
        self.assertEqual(200, response.status_code)

    def test_analysis_list(self):
        response = self.client.get(reverse(analysis_list))
        self.assertEqual(200, response.status_code)


class TestLawView(TestCase):

    def test_basic(self):
        response = self.client.get(reverse(law_list))
        self.assertEqual(200, response.status_code)

    @unittest.expectedFailure
    # TODO: this test is passing in my machine, but not in travis. Investigate.
    def test_with_law(self):
        _add_document(544590)
        _add_document(67040491)

        response = self.client.get(reverse(law_list))

        self.assertEqual(2, len(response.context['laws']))


class TestLawAnalysis(TestCase):

    def test_basic(self):
        response = self.client.get(reverse(law_analysis, args=(2,)))
        self.assertEqual(200, response.status_code)

    def test_wrong_id(self):
        response = self.client.get(reverse(law_analysis, args=(1000000,)))
        self.assertEqual(404, response.status_code)


class TestBuildContext(TestCase):

    def test_search_by_name(self):
        _add_document(544590)
        _add_document(67040491)

        context = {'laws': Document.objects.all()}

        context = build_laws_list_context(context, {'search': 'Portaria 112/2015'})

        self.assertEqual(len(context['laws']), 1)
        self.assertEqual(context['laws'][0].dre_doc_id, 67040491)

    def test_range(self):
        _add_document(544590)
        _add_document(67040491)

        context = {'laws': Document.objects.all()}

        context = build_laws_list_context(context, {'range': '1/1/2015 - 1/1/2016'})

        self.assertEqual(len(context['laws']), 1)
        self.assertEqual(context['laws'][0].dre_doc_id, 67040491)

    def test_wrong_range(self):
        _add_document(544590)
        _add_document(67040491)

        context = {'laws': Document.objects.all()}

        context = build_laws_list_context(context, {'range': '1/1/2015-1/1/2016'})

        self.assertEqual(len(context['laws']), 2)

    def test_too_high_page(self):
        context = {'laws': Document.objects.all()}
        context = build_laws_list_context(context, {'page': 100})
        self.assertEqual(len(context['laws']), 0)


class TestDataView(TestCase):

    def test_law_types_time_series_json(self):
        _add_document(544590)
        _add_document(67040491)

        response = self.client.get(reverse(analysis_selector,
                                   args=('law-types-time-series-json',)))
        self.assertEqual(200, response.status_code)

    def test_wrong_name(self):
        response = self.client.get(reverse(analysis_selector,
                                           args=('wrong-name',)))
        self.assertEqual(404, response.status_code)
