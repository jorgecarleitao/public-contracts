Organization of the code
========================

.. _django-rq: http://python-rq.org/

Django apps
-----------

The code is organized as a standard Django website composed of 4 apps:

* main: delivers ``robots.txt``, the main page, the about page, etc;
* contracts
* deputies
* law

The rest of this section, ``apps`` refer to all aps except ``main``. ``main``
is also a Django app, but does not share the common logic of the other apps.

All apps are Django-standard: they have ``models.py``, ``views.py``, ``urls.py``,
``templates``, ``static``, ``tests``.

Each app has a module called ``<app>/crawler.py`` that contains the crawler it
uses to download the data from official sources. Each app has a ``<app>/tasks
.py`` with django-rq_ jobs for running the app's crawler.

Besides a crawler, each app has a package ``<app>/analysis``. This package contains
a list of existing analysis. An analysis is just an expensive operation that is
performed once a day (after data synchronization) and is cached for 24 hours.

Since ``contracts`` is a large app, its backend is sub-divided:

* views and urls modules are divided according to whom they refer to
* templates are divided into folders, according to the view they refer to.

Scheduling
----------

We have a periodic job that runs in django-rq_ to synchronize our database with
the official sources and update caches. It uses settings from
``main/settings_for_schedule.py``.
