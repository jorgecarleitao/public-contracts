from django.core.cache import cache

import analysis


class Analysis:

    def __init__(self, name, function, timeout=60*60*24):
        self.name = name
        self.function = function
        self.timeout = timeout

    def get(self):
        result = cache.get(self.name)
        if result is None:
            result = self.update()
        return result

    def update(self):
        result = self.function()
        cache.set(self.name, result, self.timeout)
        return result


class AnalysisManager(dict):

    def register(self, analysis):
        self[analysis.name] = analysis

    def get_analysis(self, name):
        return self[name].get()

AnalysisManager = AnalysisManager()

_allAnalysis = [Analysis('municipalities_delta_time', analysis.get_municipalities_delta_time),
                Analysis('procedure_type_time_series', analysis.get_procedure_types_time_series),
                Analysis('contracts_macro_statistics', analysis.get_contracts_macro_statistics),
                Analysis('contracts_price_distribution', analysis.get_price_histogram),
                Analysis('municipalities_categories_ranking', analysis.get_municipalities_specificity),
                Analysis('municipalities_contracts_time_series', analysis.get_municipalities_contracts_time_series),
                Analysis('municipalities_procedure_types_time_series',
                         analysis.get_municipalities_procedure_types_time_series)
                ]

for x in _allAnalysis:
    AnalysisManager.register(x)
