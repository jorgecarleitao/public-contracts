import set_up
set_up.set_up_django_environment('settings')

from deputies import crawler as c
import populator as p

crawler = c.DeputiesCrawler()
populator = p.DeputiesDBPopulator()

for entry in crawler.get_new_deputies():
    deputy = populator.populate_deputy(entry)
    deputy.update()
