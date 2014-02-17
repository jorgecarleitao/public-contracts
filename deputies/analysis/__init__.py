from contracts.analysis.cache import AnalysisManager, Analysis

import analysis

_allAnalysis = [Analysis('deputies_time_distribution', analysis.get_time_in_office_distribution)]

for x in _allAnalysis:
    AnalysisManager.register(x)
