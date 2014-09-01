Organization of the code
========================

The code is organized as a standard Django website composed of 4 apps:

* main: delivers ``robots.txt``, the main page, the about page, etc;
* contracts
* deputies
* law

The rest of this section, ``apps`` refer to all aps except ``main``. ``main``
is also a Django app, but does not share the common logic of the other apps.

All apps are Django-standard: they have ``models.py``, ``views.py``, ``urls.py``,
``templates``, ``static``, ``tests``.

Each app has a module called ``app/crawler.py`` that contains the crawler it
uses to download the data from official sources.

Furthermore, each app has a package ``tools`` that contains runnable scripts.
Most notably, to populate the models (in real time) from their respective
official sources, each app has a ``tools/schedule.py`` that uses the app's
crawler.

Besides a crawler, each app has a package ``analysis``. This package contains
a list of existing analysis. An analysis is just an expensive operation that is
performed once a day (after data synchronization) and is cached for 24 hours.

Since contracts is the largest app, its backend is sub-divided:

* views and urls modules are divided according to whom they refer to
* templates are divided into folders, according to the view they refer to.

Scheduling
----------

Scheduling is made on our server using ``crontab``. The entry point from the
source code is the script ``main/tools/schedule.py``, which runs on the server
as ``cd main; python -m tools.schedule``.
