if __name__ == "__main__":
    from main.tools import set_up
    set_up.set_up_django_environment('main.settings_to_schedule')

from deputies import crawler as c
from deputies.tools import populator as p
from deputies.analysis import analysis_manager


def update():
    crawler = c.DeputiesCrawler()
    populator = p.DeputiesDBPopulator()

    for entry in crawler.get_new_deputies():
        deputy = populator.populate_deputy(entry)
        deputy.update()

    # update analysis
    for analysis in list(analysis_manager.values()):
        analysis.update()

if __name__ == "__main__":
    update()
