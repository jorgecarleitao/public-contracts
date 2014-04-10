Legislature
===========

.. _parliament website: http://www.parlamento.pt

This document provides the API references for the legislatures in the database.

.. currentmodule:: deputies

API
----

.. class:: models.Legislature

    A legislature is a time-interval between two elections.

    All the fields of this model are retrieved from `parliament website`_ using a crawler.

    .. attribute:: number

        The official number of the legislature.

    .. attribute:: date_start

        The date corresponding to the beginning of the legislature.

    .. attribute:: date_end

        The date corresponding to the end of the legislature.
        It can be null when is an ongoing legislature.
