"""
Module run every day by a cron job to update database
and cache.
"""
## setup the Django with its private settings for server.
if __name__ == "__name__":
    import set_up
    set_up.set_up_django_environment('settings_private')

from law.crawler import FirstSeriesCrawler


def update():
    crawler = FirstSeriesCrawler()
    crawler.extract_law_types()
    crawler.save_all_summaries()

if __name__ == "__name__":
    update()
