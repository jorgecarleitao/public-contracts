from main.analysis import Analysis, AnalysisManager

from contracts.analysis.analysis import *


_allAnalysis = [
    Analysis('municipalities_contracts_time_series',
             municipalities_contracts_time_series),
    Analysis('excluding_municipalities_contracts_time_series',
             exclude_municipalities_contracts_time_series),
    Analysis('municipalities_procedure_types_time_series',
             municipalities_procedure_types_time_series),
    Analysis('procedure_type_time_series', procedure_type_time_series),
    Analysis('contracts_time_series', contracts_price_time_series),
    Analysis('contracts_statistics', contracts_statistics),
    Analysis('contracts_price_distribution', contracts_price_histogram),
    Analysis('ministries_contracts_time_series', ministries_contracts_time_series),
    Analysis('entities_values_distribution', entities_values_histogram),
    Analysis('contracted_lorenz_curve', contracted_lorenz_curve),
    Analysis('municipalities_ranking', municipalities_ranking),
]


analysis_manager = AnalysisManager()
for x in _allAnalysis:
    analysis_manager.register(x)
