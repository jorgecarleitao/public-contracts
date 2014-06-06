Install development environment
===============================

This part of the documentation explains how you can jump
to the development of publicos.pt.

It assumes you know Python and a minimum of Django.

Dependencies for the website
----------------------------

Besides the :doc:`dependencies of the API <installation>`, this website
uses other packages that need to be installed:

BeautifulSoup 4
^^^^^^^^^^^^^^^

For crawling websites, we use a Python package to handle HTML elements. You need to install
it, using::

    pip install beautifulsoup4

requests
^^^^^^^^

To crawl webpages, we use the Python package requests::

    pip install requests

django-debug-toolbar (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To develop, we strongly recommend using ``django-debug-toolbar``, an
utility Django app to debug Django websites::

    pip install django-debug-toolbar

memcache (optional)
^^^^^^^^^^^^^^^^^^^

We use a caching system, memcache, to minimize database hits and store analysis.
To use it, you need to install memcache in your system, and its binding for Python::

    pip install python-memcached


Running the website
-------------------

Once you have the dependencies installed, you can run the website from the root directory using::

    python manage.py runserver

and enter in the url ``http://127.0.0.1:8000``.

.. _`mailing list`: https://groups.google.com/forum/#!forum/public-contracts

If anything went wrong or you have any question,
please drop by our `mailing list`_ so we can help you.


Running tests
-------------

We use standard Django unit test cases.
To run tests, use::

    python manage.py test <package, module, or function>

for instance, for running the test suite of contracts app, run::

    python manage.py test contracts.tests

