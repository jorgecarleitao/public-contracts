Contribute
==========

This document explains how you can contribute to this project. See why in
http://publicos.pt/contribui


Install the project for development environment
-----------------------------------------------

Deploy Python project
:::::::::::::::::::::

1. Create and start a new virtualenv::

    virtualenv ~/.virtualenvs/publicos
    source ~/.virtualenvs/publicos/bin/activate

2. Install dependencies::

    pip install -r website_requirements.txt

Deploy database locally (Optional)
::::::::::::::::::::::::::::::::::

If you develop systematically, we recommend to install the database locally so
your queries don't have to hit the production database.

1. Install and start postgres

2. Create a dump of the production database in your machine::

    pg_dump -h 5.153.9.51 -p 5432 -U publics_read_only -d publics > dump.sql

This may take some minutes as it downloads the complete database to your computer.

2. Create a new user (say `publicos` and no pass) and a database (say `publicos_db`)

3. Fill the newly created database with the dump::

    psql -U publicos -d publicos_db -f dump.sql

This also takes some time.

4. Create a file `main/settings_dev.py` and add the credentials of your database::

    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'publicos',
        'USER': 'publicos',
        }
    }

Enable searching (Optional)
:::::::::::::::::::::::::::

If you plan to test or use search capabilities in your development environment,
you need to enable searching, done via Sphinx:

.. _`Sphinx`: https://sphinxsearch.com

1. Install Sphinx_

2. Index your database::

    python manage.py index_sphinx

3. Start Sphinx daemon::

    python manage.py start_sphinx

(To stop it, call `python manage.py stop_sphinx`.)

Start your server
:::::::::::::::::

Start the server running::

    python manage.py runserver

and open a browser in `127.0.0.1:8000`.


Ticket system
-------------

.. _`ticket system`: https://github.com/jorgecarleitao/public-contracts/issues

This project uses a `ticket system`_ for documenting issues.

The system's idea is to keep track of the issues the
project has and by whom they are being addressed.

Given the size of the project, we prefer to use tickets for problems that require
some time to be solved.

Adding tickets
::::::::::::::

We write tickets with clear, concise and specific information about issue we are addressing.

Working on tickets
::::::::::::::::::

Working on the ticket means the contributor is committing himself to modify to the
source to fulfill the ticket expectations.

We give the chance to contributors - specially to new contributors -
to go thought the full process: if the person who submitted the ticket is willing to work on it,
he should have priority on doing it, even if this means having the ticket open for a longer time.

Closing tickets
:::::::::::::::

When a ticket is fixed, normally by a commit or set of commits, it is closed as fixed.
A ticket can be re-opened if there is no consensus that it was solved.

The Source Code
---------------

Code styling
::::::::::::

1. Follow PEP 8
2. Capitalize the first letter of classes.
3. Import modules in the following order:

    1. builtin modules
    2. Django modules
    3. other third party modules
    4. project modules
    5. app modules

4. Don't use::

    from X import *

5. Comment and document directly the source code only when necessary to understand
what it means within its context. The big picture is documented here.

.. hint:: Making the code clearer and better documented is a good way of start contributing to this project since
    you read code and try to make it more clear when you don't understand of it.

Documentation
:::::::::::::

A modification on the code that changes semantics of the project has to be
accompanied by the respective change in documentation to be incorporated.

.. hint:: Improving the documentation is a good way to start contributing to the project, since you learn
    about the project while improving it.


Committing
----------

When you feel that your changes provide value to the existing code, commit it.

Commit message
::::::::::::::

Use 72 characters limit to the first line of the commit message.

A commit is self contained: the first message explains what it does, the rest of the lines explain how and what
changed specifically. The actual code changes of the commit support what the commit message claims.

When the commit fixes a given ticket, it must contain that information on the commit message. E.g.

Fixed #12 -- Added support for i18n.

Pull requests
-------------

When you have a commit or set of commits that you fell are worth being incorporated (e.g.
because they close a specific ticket), make a pull request to announce that you have value that can be
added to the project.

requesting a pull
:::::::::::::::::

We prefer the GitHub way: push your local commits to your GitHub fork, and create a pull request from there.

The message of the pull request should be a message that explains that commit or set of commits.

Pull request review
:::::::::::::::::::

The idea of the pull request is that you are notifying other contributors that you
have a set of commits that are worth adding to the project.

As such, it is worth to have the pull request reviewed by other contributors before
entering the project's source. The idea is that other persons can check what you did.
