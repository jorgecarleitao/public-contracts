Category
========

.. currentmodule:: contracts

.. _CPVS: http://simap.europa.eu/codes-and-nomenclatures/codes-cpv/codes-cpv_en.htm
.. _Base: http://www.base.gov.pt/base2

This document provides the API references for the categories of contracts in
the database. See :doc:`tools/cpvs_importer` for how these categories are
built.

API References
--------------

.. class:: models.Category

    A category is an OneToMany relationship to :class:`~models.Contract`: each
    contract has one category, each category can have more than one contract.
    This relationship is thus defined in the contract model.

    It has the following attributes:

    .. attribute:: code

        The CPVS_ code of the category.

    .. attribute:: description_en
    .. attribute:: description_pt

        The official descriptions of the category in english and portuguese,
        respectively.

    .. attribute:: depth

        The depth of the attribute on the tree.

    And has the following methods:

    .. method:: get_children()

        Returns all children categories, excluding itself.

    .. method:: get_ancestors()

        Returns all ancestor categories, excluding itself.

    .. method:: get_absolute_url()

        Returns the url of this category in the website.

    .. method:: contracts_count()

        Counts the number of all contracts that belong to this category or any
        of its children.

    .. method:: contracts_price()

        Sums the prices of all contracts that belong to this category or any of
        its children.
