import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.core.cache import cache


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

    def get_analysis(self, name, flush=False):
        if flush:
            self[name].update()
        return self[name].get()
