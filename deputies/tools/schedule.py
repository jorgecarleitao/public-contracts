if __name__ == "__main__":
    from . import set_up
    set_up.set_up_django_environment('settings_private')

from deputies import crawler as c
from . import populator as p


def update():
    crawler = c.DeputiesCrawler()
    populator = p.DeputiesDBPopulator()

    for entry in crawler.get_new_deputies():
        deputy = populator.populate_deputy(entry)
        deputy.update()

if __name__ == "__main__":
    update()
