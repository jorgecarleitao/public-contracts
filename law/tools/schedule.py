"""
Module run every day by a cron job to update database and cache.
"""
if __name__ == "__main__":
    from main.tools import set_up
    set_up.set_up_django_environment('main.settings_for_schedule')

from law.crawler import FirstSeriesCrawler, Populator
from law.analysis import analysis_manager


def update():
    import datetime
    current_year = datetime.datetime.now().date().year
    for year in range(current_year - 1, current_year + 1):
        crawler = FirstSeriesCrawler()
        crawler.get_documents(year)
        del crawler

    p = Populator()
    p.populate_all(current_year - 1)

    update_cache()


def update_cache():
    # update analysis
    for analysis in list(analysis_manager.values()):
        analysis.update()


if __name__ == "__main__":
    update()
