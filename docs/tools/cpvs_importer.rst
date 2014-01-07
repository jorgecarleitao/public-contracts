CPVS importer
==============

.. currentmodule:: cpvs

.. _Base: http://www.base.gov.pt/base2
.. _CPVS: http://simap.europa.eu/codes-and-nomenclatures/codes-cpv/codes-cpv_en.htm
.. _tree: https://en.wikipedia.org/wiki/Tree_(data_structure)
.. _`nested set`: https://en.wikipedia.org/wiki/Nested_set_model

This document documents how we build the database of categories, and how we create a tree out of it.

Europe Union has a categorisation system for public contracts, CPVS_, that translates a string of 8 digits
into a category to be used in public contracts.

More than categories, the system builds a tree_ with broader categories like "agriculture",
and more specific ones like "potatos". For more information, see CPVS_.

In their website, they provide an .xml file with all these categories.
We use it to build our database.

We have two methods:

.. function:: build_cpvs([file_path])

    Imports the file to a python xml.etree.ElementTree and saves each CPV into a table for CPVs.
    If the CPV already exists, it skips it.

    The optional file_path defaults to '../data/cpv_2008.xml'

.. function:: build_tree()

    Builds the tree of CPVs from the table of CPVs.

    Filters the most general category, and saves it. Associates each of the more
    specific categories within the general category, and saves then. Repeats this for all the levels.
