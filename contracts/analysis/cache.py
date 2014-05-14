# coding=utf-8
from __future__ import unicode_literals
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.core.cache import cache

from . import analysis


class TwoWayDict(dict):
    """
    http://stackoverflow.com/a/13276237/931303
    """
    def __setitem__(self, key, value):
        # Remove any previous connections with these values
        if key in self:
            del self[key]
        if value in self:
            del self[value]
        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)

    def __len__(self):
        """Returns the number of connections"""
        # The int() call is for Python 3
        return int(dict.__len__(self) / 2)


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
        logger.info('Updating analysis "%s"', self.name)
        result = self.function(*self.args, **self.kwargs)
        cache.set(self.name, result, 60*60*24)
        return result


class AnalysisManager(dict):

    def register(self, analysis, primary_key=None):
        analysis.idem = primary_key
        self[analysis.name] = analysis

    def get_analysis(self, name):
        return self[name].get()

AnalysisManager = AnalysisManager()

_allAnalysis = [Analysis('municipalities_delta_time', analysis.get_entities_delta_time,
                         'Município'),
                Analysis('municipalities_contracts_time_series', analysis.get_entities_contracts_time_series,
                         'Município'),
                Analysis('excluding_municipalities_contracts_time_series', analysis.get_excluding_entities_contracts_time_series,
                         'Município'),
                Analysis('municipalities_categories_ranking', analysis.get_entities_specificity,
                         'Município'),
                Analysis('municipalities_procedure_types_time_series', analysis.get_procedure_types_time_series,
                         'Município'),
                Analysis('procedure_type_time_series', analysis.get_all_procedure_types_time_series),
                Analysis('contracts_time_series', analysis.get_contracts_price_time_series),
                Analysis('contracts_macro_statistics', analysis.get_contracts_macro_statistics),
                Analysis('contracts_price_distribution', analysis.get_price_histogram),
                Analysis('ministries_contracts_time_series', analysis.get_entities_contracts_time_series,
                         'Secretaria-Geral do Ministério'),
                Analysis('ministries_delta_time', analysis.get_entities_delta_time,
                         'Secretaria-Geral do Ministério'),

                Analysis('legislation_application_time_series', analysis.get_legislation_application_time_series)
]

for x in _allAnalysis:
    AnalysisManager.register(x)
