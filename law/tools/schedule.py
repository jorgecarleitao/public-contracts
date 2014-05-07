"""
Module run every day by a cron job to update database
and cache.
"""
## setup the Django with its private settings for server.
if __name__ == "__main__":
    from . import set_up
    set_up.set_up_django_environment('law.tools.settings_private')

from law.crawler import FirstSeriesCrawler, Populator


def update():
    import datetime
    current_year = datetime.datetime.now().date().year
    for year in range(current_year - 1, current_year + 1):
        crawler = FirstSeriesCrawler()
        crawler.get_documents(year)
        del crawler

    p = Populator()
    p.populate_all(current_year - 1)

if __name__ == "__main__":
    update()
