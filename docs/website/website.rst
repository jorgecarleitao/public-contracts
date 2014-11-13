Install development environment
===============================

This part of the documentation explains how you can jump to the development of
publicos.pt and deploy the website on your computer. To only interact with the
database, e.g. to do statistics, you only need to
:doc:`install the API dependencies <../installation>`.

We assume here that you know Python and a minimum of Django.

Dependencies for the website
----------------------------

Besides the :doc:`dependencies of the API <../installation>`, the website uses
the following packages:

BeautifulSoup 4
^^^^^^^^^^^^^^^

For crawling websites, we use a Python package to handle HTML elements. To
install it, use::

    pip install beautifulsoup4

django-debug-toolbar
^^^^^^^^^^^^^^^^^^^^

To develop, we use ``django-debug-toolbar``, an utility to debug Django websites::

    pip install django-debug-toolbar

Running the website
-------------------

Once you have the dependencies installed, you can run the website from the root
directory using::

    python manage.py runserver

and enter in the url ``http://127.0.0.1:8000``.

.. _`mailing list`: https://groups.google.com/forum/#!forum/public-contracts

If anything went wrong or you have any question,
please drop by our `mailing list`_ so we can help you.


Running tests
-------------

We use standard Django unit test cases. To run tests, use::

    python manage.py test <package, module, or function>

For instance, for running the test suite of contracts app, run::

    python manage.py test contracts.tests


Running the crawler
-------------------

To run the :doc:`../tools/crawler` to populate the database,
you require an additional package::

    pip install requests

