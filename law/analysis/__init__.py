from collections import defaultdict

from contracts.analysis.cache import AnalysisManager, Analysis

from law.analysis.analysis import get_documents_time_series, get_eu_impact_time_series


_allAnalysis = [
    Analysis('law_count_time_series', get_documents_time_series),
    Analysis('law_eu_impact_time_series', get_eu_impact_time_series)]

ANALYSIS = {'law_count_time_series': 1,
            'law_eu_impact_time_series': 2}

PRIMARY_KEY = dict()
for k, v in ANALYSIS.items():
    PRIMARY_KEY[v] = k

for x in _allAnalysis:
    AnalysisManager.register(x, primary_key=ANALYSIS[x.name])
