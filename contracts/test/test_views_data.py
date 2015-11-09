from datetime import datetime, date

import django.test

from contracts.models import Contract, Entity, ProcedureType
from contracts.views_data import *
from contracts.views_analysis import ANALYSIS


class TestAnalysis(django.test.TestCase):

    def test_contracts_price_histogram(self):
        Contract.objects.create(
            base_id=1, contract_description='da', price=1000,
            added_date=datetime(year=2003, month=1, day=1),
            signing_date=datetime(year=2003, month=1, day=1))

        response = self.client.get(
            reverse(analysis_selector, args=('contracts-price-histogram-json',)))
        self.assertEqual(200, response.status_code)

        self.assertEqual([{'values': [], 'key': 'histogram of contracts values'}],
                         json.loads(response.content.decode('utf-8')))

        Contract.objects.all().delete()
        for x in range(10):
            Contract.objects.create(
                base_id=x, contract_description='da', price=1000,
                added_date=datetime(year=2003, month=1, day=1),
                signing_date=datetime(year=2003, month=1, day=1))

        response = self.client.get(
            reverse(analysis_selector, args=('contracts-price-histogram-json',)))
        self.assertEqual(200, response.status_code)

        self.assertEqual([{'values': [{'min_value': 8, 'max_value': 16,
                                       'count': 10}],
                           'key': 'histogram of contracts values'}],
                         json.loads(response.content.decode('utf-8')))

    def test_entities_values_histogram(self):
        c = Contract.objects.create(
            base_id=1, contract_description='da', price=1000,
            added_date=datetime(year=2003, month=1, day=1),
            signing_date=datetime(year=2003, month=1, day=1))

        e1 = Entity.objects.create(name='test1', base_id=1, nif='nif')
        e2 = Entity.objects.create(name='test2', base_id=2, nif='nif')

        c.contractors.add(e1)
        c.contracted.add(e2)

        e1.compute_data()
        e2.compute_data()

        response = self.client.get(
            reverse(analysis_selector, args=('entities-values-histogram-json',)))
        self.assertEqual(200, response.status_code)

        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual({'values': [{'value': 1, 'min_value': 8, 'max_value': 16}],
                          'key': 'entities earning'},
                         result[0])

        self.assertEqual({'values': [{'value': 0, 'min_value': 8, 'max_value': 16}],
                          'key': 'entities expending'},
                         result[1])

    def test_contracts_statistics(self):
        Contract.objects.create(
            base_id=1, contract_description='da', price=1000,
            added_date=datetime(year=2003, month=1, day=1),
            signing_date=datetime(year=2003, month=1, day=1))

        today = date.today()

        Contract.objects.create(
            base_id=2, contract_description='da', price=1000,
            added_date=datetime(year=today.year, month=today.month, day=1),
            signing_date=datetime(year=today.year, month=today.month, day=1))

        data = analysis_manager.get_analysis("contracts_statistics")

        self.assertEqual(data['total_sum'], 2000)
        self.assertEqual(data['total_count'], 2)
        self.assertEqual(data['year_sum'], 1000)
        self.assertEqual(data['year_count'], 1)
        self.assertEqual(data['month_sum'], 1000)
        self.assertEqual(data['month_count'], 1)

    def test_ProceduresTimeSeriesJsonView(self):

        # e1 is a municipality
        e1 = Entity.objects.create(name='test1', base_id=1, nif='506572218')
        e2 = Entity.objects.create(name='test2', base_id=2, nif='nif')

        p1 = ProcedureType.objects.create(name='Test1', base_id=1)
        p2 = ProcedureType.objects.create(name='Test2', base_id=2)

        c1 = Contract.objects.create(
            base_id=1, contract_description='da', price=1000,
            added_date=datetime(year=2011, month=1, day=1),
            signing_date=datetime(year=2011, month=1, day=1),
            procedure_type=p1,
        )

        c1.contractors.add(e1)
        c1.contracted.add(e2)

        c2 = Contract.objects.create(
            base_id=2, contract_description='da', price=2000,
            added_date=datetime(year=2011, month=2, day=1),
            signing_date=datetime(year=2011, month=2, day=1),
            procedure_type=p2,
        )

        c2.contractors.add(e1)
        c2.contracted.add(e2)

        # contract without date should not count anywhere
        Contract.objects.create(
            base_id=3, contract_description='da', price=2000,
            added_date=datetime(year=2011, month=2, day=1),
            signing_date=None,
            procedure_type=p2,
        )

        expected = [{'key': 'Test1', 'values':
            [{'value': 10, 'month': '2011-01', 'count': 1},
             {'value': 0, 'month': '2011-02', 'count': 0}
             ]},
                    {'key': 'Test2', 'values':
                        [{'value': 0, 'month': '2011-01', 'count': 0},
                         {'value': 20, 'month': '2011-02', 'count': 1},
                         ]}
                    ]

        response = self.client.get(
            reverse(analysis_selector, args=('procedure-types-time-series-json',)))
        self.assertEqual(200, response.status_code)

        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual(expected, result)

        # since e1 is municipality, the outcome should be the same
        response = self.client.get(
            reverse(analysis_selector, args=('municipalities-procedure-types-'
                                             'time-series-json',)))
        self.assertEqual(200, response.status_code)

        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual(expected, result)

    def test_ContractsTimeSeriesJsonView(self):

        # e1 is a municipality
        e1 = Entity.objects.create(name='test1', base_id=1, nif='506572218')
        e2 = Entity.objects.create(name='test2', base_id=2, nif='nif')

        c1 = Contract.objects.create(
            base_id=1, contract_description='da', price=1000,
            added_date=datetime(year=2011, month=1, day=1),
            signing_date=datetime(year=2011, month=1, day=1),
        )

        c1.contractors.add(e1)
        c1.contracted.add(e2)

        c2 = Contract.objects.create(
            base_id=2, contract_description='da', price=2000,
            added_date=datetime(year=2011, month=2, day=1),
            signing_date=datetime(year=2011, month=2, day=1),
        )

        c2.contractors.add(e1)
        c2.contracted.add(e2)

        response = self.client.get(
            reverse(analysis_selector, args=('municipalities-contracts-time-'
                                             'series-json',)))
        self.assertEqual(200, response.status_code)

        result = json.loads(response.content.decode('utf-8'))

        expected = [{'key': 'contracts', 'bar': True, 'values':
            [{'value': 1, 'month': '2011-01'},
             {'value': 1, 'month': '2011-02'},
             ]},
                    {'key': 'value', 'color': 'black', 'values':
                        [{'value': 10, 'month': '2011-01'},
                         {'value': 20, 'month': '2011-02'}
                         ]}
                    ]

        self.assertEqual(expected, result)

        response = self.client.get(
            reverse(analysis_selector, args=('contracts-time-series-json',)))
        self.assertEqual(200, response.status_code)

        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual(expected, result)

        response = self.client.get(
            reverse(analysis_selector, args=('excluding-municipalities-contracts-'
                                             'time-series-json',)))
        self.assertEqual(200, response.status_code)

        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual([{'key': 'contracts', 'bar': True, 'values': []},
                          {'key': 'value', 'color': 'black', 'values': []}],
                         result)

        # change e1 to a ministry
        e1.name = 'Secretaria-Geral do Ministério da Educação'
        e1.save()

        response = self.client.get(
            reverse(analysis_selector, args=('ministries-contracts-'
                                             'time-series-json',)))
        self.assertEqual(200, response.status_code)

        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual(expected, result)

    def test_lorenz_curve(self):
        # e1 always contracts; e2 and e3 receive
        e1 = Entity.objects.create(name='test1', base_id=1, nif='nif')
        e2 = Entity.objects.create(name='test2', base_id=2, nif='nif')
        e3 = Entity.objects.create(name='test2', base_id=3, nif='nif')

        c1 = Contract.objects.create(
            base_id=1, contract_description='da', price=1000,
            added_date=datetime(year=2010, month=1, day=1),
            signing_date=datetime(year=2010, month=1, day=1))

        c1.contractors.add(e1)
        c1.contracted.add(e2)

        c2 = Contract.objects.create(
            base_id=2, contract_description='da', price=2000,
            added_date=datetime(year=2010, month=1, day=1),
            signing_date=datetime(year=2010, month=1, day=1))

        c2.contractors.add(e1)
        c2.contracted.add(e3)

        e1.compute_data()
        e2.compute_data()
        e3.compute_data()

        response = self.client.get(
            reverse(analysis_selector, args=('contracted-lorenz-curve-json',)))
        self.assertEqual(200, response.status_code)

        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual({'values': [{'cumulative': 0.0, 'rank': 0.0},
                                     {'cumulative': 1.0, 'rank': 1.0}],
                          'key': 'Equality line'},
                         result[0])
        self.assertEqual({'values': [{'cumulative': 0.3333333333333333, 'rank': 0.0},
                                     {'cumulative': 1.0, 'rank': 1.0}],
                          'key': 'Lorenz curve of private entities'},
                         result[1])

    def test_municipalities_ranking(self):
        # e1 and e2 are municipalities
        e1 = Entity.objects.create(name='test1', base_id=1, nif='506780902')
        e2 = Entity.objects.create(name='test2', base_id=2, nif='506572218')

        c1 = Contract.objects.create(
            base_id=1, contract_description='da', price=1000,
            added_date=datetime(year=2010, month=1, day=3),
            signing_date=datetime(year=2010, month=1, day=1),
            description='BlaBla')

        c1.contractors.add(e1)

        c2 = Contract.objects.create(
            base_id=2, contract_description='da', price=2000,
            added_date=datetime(year=2010, month=2, day=1),
            signing_date=datetime(year=2010, month=2, day=1))

        c2.contractors.add(e2)

        c3 = Contract.objects.create(
            base_id=3, contract_description='da', price=3000,
            added_date=datetime(year=2011, month=2, day=1),
            signing_date=datetime(year=2011, month=2, day=1))

        c3.contractors.add(e2)

        response = self.client.get(
            reverse(analysis_selector, args=('municipalities-ranking-json',)))
        self.assertEqual(200, response.status_code)

        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual('Cartaxo', result[0]['key'])
        self.assertEqual('/entity/id1/cartaxo', result[0]['url'])

        self.assertEqual(2, len(result[0]['values']))

        self.assertEqual({'avg_deltat_rank': 2,
                          'avg_specificity': 0.0,
                          'avg_good_text': 1.0,
                          'avg_good_text_rank': 1,
                          'avg_deltat': 2.0,
                          'year': '2010',
                          'avg_specificity_rank': 1,
                          'count': 1,
                          'value': 10.0}, result[0]['values'][0])

        self.assertEqual({'avg_deltat_rank': None,
                          'avg_specificity': None,
                          'avg_good_text': None,
                          'avg_good_text_rank': None,
                          'avg_deltat': None,
                          'year': '2011',
                          'avg_specificity_rank': None,
                          'count': 0,
                          'value': 0}, result[0]['values'][1])

        self.assertEqual('Lamego', result[1]['key'])
        self.assertEqual('/entity/id2/lamego', result[1]['url'])

        self.assertEqual(2, len(result[1]['values']))

        self.assertEqual({'avg_deltat_rank': 1,
                          'avg_specificity': 0.0,
                          'avg_good_text': 0.0,
                          'avg_good_text_rank': 2,
                          'avg_deltat': 0.0,
                          'year': '2010',
                          'avg_specificity_rank': 1,
                          'count': 1,
                          'value': 20.0}, result[1]['values'][0])

        self.assertEqual({'avg_deltat_rank': 1,
                          'avg_specificity': 0.0,
                          'avg_good_text': 0.0,
                          'avg_good_text_rank': 1,
                          'avg_deltat': 0,
                          'year': '2011',
                          'avg_specificity_rank': 1,
                          'count': 1,
                          'value': 30.0}, result[1]['values'][1])

    def test_data_not_found(self):
        response = self.client.get(reverse(analysis_selector,
                                           args=('invalid-name',)))
        self.assertEqual(404, response.status_code)


class TestAnalysisViews(django.test.TestCase):

    def test_views(self):
        for name in ANALYSIS:
            identity = ANALYSIS[name]['id']
            title = ANALYSIS[name]['title']

            response = self.client.get(
                reverse('contracts_analysis_selector',
                        args=(identity, slugify(title))))
            self.assertEqual(200, response.status_code)

        response = self.client.get(
            reverse('contracts_analysis_selector', args=(10000, 'bla')))
        self.assertEqual(302, response.status_code)

    def test_analysis_list(self):
        response = self.client.get(reverse('contracts_analysis'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(ANALYSIS), len(response.context['analysis']))
