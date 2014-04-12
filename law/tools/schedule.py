"""
Module run every day by a cron job to update database
and cache.
"""
## setup the Django with its private settings for server.
if __name__ == "__main__":
    import set_up
    set_up.set_up_django_environment('law.tools.settings_private')

from law.crawler import FirstSeriesCrawler


def update():
    crawler = FirstSeriesCrawler()
    crawler.extract_law_types()
    crawler.update_all()

if __name__ == "__main__":
    update()
