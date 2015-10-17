# coding=utf-8
from __future__ import unicode_literals

from main.analysis import Analysis, AnalysisManager

from contracts.analysis.analysis import *


_allAnalysis = [Analysis('municipalities_delta_time',
                         municipalities_delta_time),
                Analysis('municipalities_contracts_time_series',
                         municipalities_contracts_time_series),
                Analysis('excluding_municipalities_contracts_time_series',
                         exclude_municipalities_contracts_time_series),
                Analysis('municipalities_categories_ranking',
                         get_municipalities_specificity),
                Analysis('municipalities_procedure_types_time_series',
                         municipalities_procedure_types_time_series),
                Analysis('procedure_type_time_series', procedure_types_time_series),
                Analysis('contracts_time_series', contracts_price_time_series),
                Analysis('contracts_macro_statistics', get_contracts_macro_statistics),
                Analysis('contracts_price_distribution', get_price_histogram),
                Analysis('ministries_contracts_time_series', ministries_contracts_time_series),
                Analysis('ministries_delta_time', ministries_delta_time),
                Analysis('legislation_application_time_series',
                         get_legislation_application_time_series),
                Analysis('entities_values_distribution',
                         get_entities_value_histogram),
                Analysis('contracted_lorenz_curve',
                         get_lorenz_curve)
                ]

ANALYSIS = {'municipalities_delta_time': 1,
            'municipalities_contracts_time_series': 2,
            'excluding_municipalities_contracts_time_series': 3,
            'municipalities_categories_ranking': 4,
            'municipalities_procedure_types_time_series': 5,
            'procedure_type_time_series': 6,
            'contracts_time_series': 7,
            'contracts_macro_statistics': 8,
            'contracts_price_distribution': 9,
            'ministries_contracts_time_series': 10,
            'ministries_delta_time': 11,
            'legislation_application_time_series': 12,
            'entities_values_distribution': 13,
            'contracted_lorenz_curve': 14
            }

PRIMARY_KEY = dict()
for k, v in ANALYSIS.items():
    PRIMARY_KEY[v] = k

analysis_manager = AnalysisManager()
for x in _allAnalysis:
    analysis_manager.register(x, primary_key=ANALYSIS[x.name])
