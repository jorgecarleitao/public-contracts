Crawler
=======

.. currentmodule:: contracts

.. _Base: http://www.base.gov.pt/base2
.. _mechanize: http://wwwsearch.sourceforge.net/mechanize/

.. important::
    We don't provide the source of the crawler as it can be inadvertently used to cause
    Denial of Service (DoS) to Base_ database. The documentation is for the sake of explaining what it does.

This document explains how Base_ provides its data and what our crawler does.

.. note::
    If you want the information from Base_, consider retrieving them from our
    :doc:`database <tools/database>` or from http://www.dados.gov.pt/.

Base database
---------------

Base uses the following urls to provide its data

- :class:`~models.Entity`: http://www.base.gov.pt/base2/rest/entidades/[base_id]
- :class:`~models.Contract`: http://www.base.gov.pt/base2/rest/contratos/[base_id]
- List of countries: http://www.base.gov.pt/base2/rest/lista/paises
- List of districts: http://www.base.gov.pt/base2/rest/lista/distritos?pais=[country_base_id]; (portugal_base_id=187)
- List of councils: http://www.base.gov.pt/base2/rest/lista/concelhos?distrito=[district_base_id];
- List of types of contracts: http://www.base.gov.pt/base2/rest/lista/tipocontratos
- List of types of procedures: http://www.base.gov.pt/base2/rest/lista/tipoprocedimentos
- List of 25 entities: http://www.base.gov.pt/base2/rest/entidades [1]
- List of 25 contracts: http://www.base.gov.pt/base2/rest/contratos [1]

The lists of :class:`entities <models.Entity>` and :class:`contracts <models.Contract>` grow over time,
the others are constant and only have to be retrieved once.

Each url returns a :mod:`json` object with respective information. The objective of our crawler is two fold:
One one hand, it retrieves the contracts and entities :attr:`~contracts.models.Contract.base_id` from
the lists of contracts and entities,
on the other hand, it validates the :mod:`json` data and construct the database entries with the validated data.


[1] Both lists returns 25 elements. Which specific elements are to be retrieved have to be defined
in the header of the request.

.. currentmodule:: contracts.crawler


What our crawler does
-------------------------

The crawler accesses Base_ webpages and uses the following procedure:

1. Crawls the list of entities to retrieve their information, validates it, and stores it in the database.
2. Crawls the list of contracts to get all their 'base_id's.
3. Crawls each contract to retrieve its information, validates it, and stores it in the database.

Because Base_ database is constantly being updated with new contracts and entities, this procedure is daily repeated.
To avoid hitting Base_ with extra queries, the crawler remembers the last entity and contract retrieved,
continuing from that one on posterior calls.


API
-----

.. class:: Crawler

    An object that can crawl the Base_.

    .. attribute:: browser

        The mechanize_ browser

    .. method:: update_contracts()

        Updates the database by retrieving :class:`contracts <contracts.models.Contract>` from Base_.

        First, it hits Base_ database to retrieve 25 contracts :attr:`~contracts.models.Contract.base_id`,
        saving these on a file.
        Next, it hits the Base_ database for each entry in the block, saving these on a file.
        Finally, it creates a database entry (if it doesn't exist) for each :class:`contract <contracts.models.Contract>`
        on the block. This is repeated until a retrieved block returns no entries.

        Subsequent calls of this function start from the last unfilled block, avoiding further hits on Base_ database.

    .. method:: update_entities()

        Updates the database by retrieving :class:`entities <contracts.models.Entity>` from Base_.

        Similar to :meth:`update_contracts` but for :class:`entities <contracts.models.Entity>`. However,
        it only hits Base_ database for getting the block of 25 entities because Base_ interface already provides
        the relevant information of the entity in the list.

        Like update_contracts, this method also saves the retrieved information in files.

    .. method:: retrieve_and_save_contracts_types()
    .. method:: retrieve_and_save_procedures_types()
    .. method:: retrieve_and_save_countries()
    .. method:: retrieve_and_save_districts(country)
    .. method:: retrieve_and_save_councils(district)

        Methods used to retrieve other tables for contracts and entities. They only have to be called once
        during the database construction.


Dependencies for the crawler
----------------------------------

Mechanize
^^^^^^^^^^^^^^^^^

The crawler depends on mechanize_. It can be installed using::

    pip install mechanize

