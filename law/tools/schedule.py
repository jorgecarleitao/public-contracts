"""
Module run every day by a cron job to update database
and cache.
"""
## setup the Django with its private settings for server.
if __name__ == "__main__":
    import set_up
    set_up.set_up_django_environment('law.tools.settings_private')

from law.crawler import FirstSeriesCrawler


if __name__ == "__main__":
    for year in range(1910, 2015):
        crawler = FirstSeriesCrawler()
        crawler.get_documents(year)
        del crawler
