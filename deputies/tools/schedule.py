import set_up
set_up.set_up_django_environment('settings')

from deputies import crawler as c
import populator as p

crawler = c.DeputiesCrawler()
populator = p.DeputiesDBPopulator()

for entry in crawler.get_deputies():
    populator.populate_deputy(entry)

from deputies import models

for deputy in models.Deputy.objects.all():
    deputy.update()

#for entry in interests_crawler.crawl_conflicts(flush_cache=True):
#    print entry
#for entry in interests_crawler.crawl_activities(flush_cache=False):
#    print entry
