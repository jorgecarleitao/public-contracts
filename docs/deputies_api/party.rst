Party
=====

.. _parliament website: http://www.parlamento.pt

This document provides the API references for the parties in the database.

.. currentmodule:: deputies

API
----

.. class:: models.Party

    A party, formally known as a Parlamentary Group, is required to have a mandate in the parliament.
    Here is just a category of the mandate.

    All fields of this model are retrieved from `parliament website`_ using a crawler.

    .. attribute:: abbrev

        The abbreviated name of the party.

    .. method:: get_absolute_url

        The url for its view on the website.
