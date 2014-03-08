# coding=utf-8
from django.core.cache import cache

import analysis


class Analysis:

    def __init__(self, name, function, *args, **kwargs):
        self.name = name
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def get(self):
        result = cache.get(self.name)
        if result is None:
            result = self.update()
        return result

    def update(self):
        result = self.function(*self.args, **self.kwargs)
        cache.set(self.name, result, 60*60*24)
        return result


class AnalysisManager(dict):

    def register(self, analysis):
        self[analysis.name] = analysis

    def get_analysis(self, name):
        return self[name].get()

AnalysisManager = AnalysisManager()

_allAnalysis = [Analysis('municipalities_delta_time', analysis.get_entities_delta_time,
                         u'Município'),
                Analysis('municipalities_contracts_time_series', analysis.get_entities_contracts_time_series,
                         u'Município'),
                Analysis('excluding_municipalities_contracts_time_series', analysis.get_excluding_entities_contracts_time_series,
                         u'Município'),
                Analysis('municipalities_categories_ranking', analysis.get_entities_specificity,
                         u'Município'),
                Analysis('municipalities_procedure_types_time_series', analysis.get_procedure_types_time_series,
                         u'Município'),
                Analysis('procedure_type_time_series', analysis.get_all_procedure_types_time_series),
                Analysis('contracts_time_series', analysis.get_contracts_price_time_series),
                Analysis('contracts_macro_statistics', analysis.get_contracts_macro_statistics),
                Analysis('contracts_price_distribution', analysis.get_price_histogram),
                Analysis('ministries_contracts_time_series', analysis.get_entities_contracts_time_series,
                         u'Secretaria-Geral do Ministério'),
                Analysis('ministries_delta_time', analysis.get_entities_delta_time,
                         u'Secretaria-Geral do Ministério'),

                Analysis('legislation_application_time_series', analysis.get_legislation_application_time_series)
]

for x in _allAnalysis:
    AnalysisManager.register(x)
