Deputy
======

.. _parliament website: http://www.parlamento.pt

This document provides the API references for the deputies in the database.

.. currentmodule:: deputies

API
----

.. class:: models.Deputy

    A deputy is a person that at some point was part of the parliament.

    All the fields of this model are retrieved from `parliament website`_ using a crawler.

    .. attribute:: name

        The name of the person.

    .. attribute:: birthday

        Birthday of the person. May be null if it is not in the official database.

    .. attribute:: party

        A foreign key to the party the deputy belongs. This is a cached version, the correct
         version is always obtained from the mandate the deputy is.

    .. attribute:: is_active

        A bool telling if the deputy is active or not. This is a cached version, the correct
        value is always obtained from the last mandate the deputy is.

    .. method:: get_absolute_url()

        Returns the url of this entity in `parliament website`_.

    .. method:: update()

        Updates the :attr:`party` and :attr:`is_active` using the deputies' last mandate information.
        This only has to be called when the deputy has a new mandate.
