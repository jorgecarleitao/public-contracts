from deputies import crawler as c
from deputies.tools import populator as p
from deputies.analysis import analysis_manager

from django_rq import job


@job
def update_deputies():
    # check if we need to download static data
    crawler = c.DeputiesCrawler()
    populator = p.DeputiesDBPopulator()

    for entry in crawler.iterate_deputies():
        deputy = populator.populate_deputy(entry)
        deputy.update()


@job
def recompute_analysis():
    # update analysis
    for analysis in list(analysis_manager.values()):
        analysis.update()


@job
def update():
    update_deputies()
    recompute_analysis()
