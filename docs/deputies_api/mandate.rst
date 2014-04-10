Mandate
=======

.. _parliament website: http://www.parlamento.pt

This document provides the API references for the mandates in the database.

.. currentmodule:: deputies

API
----

.. class:: models.Mandate

    A mandate is a time-interval corresponding to a mandate in the parliament of a deputy.
    A mandate require always a district and a party.

    All the fields of this model are retrieved from `parliament website`_ using a crawler.

    .. attribute:: deputy

        The :class:`models.Deputy` of the mandate.

    .. attribute:: legislature

        The :class:`models.Legislature` of the mandate.

    .. attribute:: party

        The parlamentary group this mandate is respective to. A ForeignKey to :class:`models.Party`.

    .. attribute:: district

        The district this mandate is respective to. This is a ForeignKey to :class:`models.District`.

    The next two fields are required because some mandates end before the legislature ends.

    .. attribute:: date_start

        The date corresponding to the beginning of the mandate.

    .. attribute:: date_end

        The date corresponding to the end of the mandate.
        It can be null when is an ongoing legislature.
