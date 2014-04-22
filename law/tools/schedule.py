"""
Module run every day by a cron job to update database
and cache.
"""
## setup the Django with its private settings for server.
if __name__ == "__main__":
    import set_up
    set_up.set_up_django_environment('law.tools.settings_private')

from law.crawler import FirstSeriesCrawler, Populator


def update():
    for year in range(1910, 2015):
        crawler = FirstSeriesCrawler()
        crawler.get_documents(year)
        del crawler

    p = Populator()
    p.populate_all(1910)
