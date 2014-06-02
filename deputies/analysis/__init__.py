from main.analysis import AnalysisManager, Analysis

from deputies.analysis.analysis import *

_allAnalysis = [Analysis('deputies_time_distribution', get_time_in_office_distribution),
                Analysis('mandates_distribution', get_mandates_in_office_distribution)]


ANALYSIS = {'deputies_time_distribution': 1,
            'mandates_distribution': 2}

PRIMARY_KEY = dict()
for k, v in ANALYSIS.items():
    PRIMARY_KEY[v] = k

analysis_manager = AnalysisManager()
for x in _allAnalysis:
    analysis_manager.register(x, primary_key=ANALYSIS[x.name])
