Crawler
=======

.. currentmodule:: contracts.crawler

.. _Base: http://www.base.gov.pt/base2
.. _mechanize: http://wwwsearch.sourceforge.net/mechanize/

This document explains how Base_ provides its data and what our crawler works.

.. important::
    Please, avoid using the crawler on your own as it can generate Denial of Service (DoS) to Base_ database.
    We provide remote access to ours exactly to avoid that.

Base database
---------------

Base_ uses the following urls to expose its data

- :class:`~models.Entity`: http://www.base.gov.pt/base2/rest/entidades/[base_id]
- :class:`~models.Contract`: http://www.base.gov.pt/base2/rest/contratos/[base_id]
- List of countries: http://www.base.gov.pt/base2/rest/lista/paises
- List of districts: http://www.base.gov.pt/base2/rest/lista/distritos?pais=[country_base_id]; (portugal_base_id=187)
- List of councils: http://www.base.gov.pt/base2/rest/lista/concelhos?distrito=[district_base_id];
- List of types of contracts: http://www.base.gov.pt/base2/rest/lista/tipocontratos
- List of types of procedures: http://www.base.gov.pt/base2/rest/lista/tipoprocedimentos
- List of 25 entities: http://www.base.gov.pt/base2/rest/entidades [1]
- List of 25 contracts: http://www.base.gov.pt/base2/rest/contratos [1]

[1] Both lists returns 25 elements. Which specific elements to be retrieved have to be defined
in the header of the request.

Each url returns a :mod:`json` object with respective information. For this reason,
we have an abstract crawler for retrieving json from urls:

The lists of entities and contracts grow over time, the others are constant and only have to be retrieved once.

What our crawler does
-------------------------

The crawler accesses Base_ urls using the following procedure:

1. Crawls the list of entities to retrieve their information, validates it, and stores it in the database.
2. Crawls the list of contracts to get all their 'base_id's.
3. Crawls each contract to retrieve its information, validates it, and stores it in the database.

Because Base_ database is constantly being updated with new contracts and entities,
this procedure is repeated once a day.
To avoid hitting Base_ with extra queries, the crawler remembers the last entity and contract retrieved,
continuing from that one on posterior calls.


API
-----

.. class::AbstractCrawler

    An object able to retrieve JSON content from an url. When initialized, it initializes a mechanize_ browser.
    It has one method:

    .. method:: goToPage(url)

        Returns a dictionary loaded with json from the url.

For retrieving data, the procedure is separated in three steps:

1. Go to the url and retrieve the data
2. Validate the data
3. Populate the database with the validated data.

For static data, this is relatively easy. We provide a specific crawler for this:

.. class:: StaticDataCrawler

    This crawler only needs to be run once. It is used to populate the database:

    .. method:: retrieve_and_save_contracts_types()
    .. method:: retrieve_and_save_procedures_types()
    .. method:: retrieve_and_save_countries()
    .. method:: retrieve_and_save_districts(country)
    .. method:: retrieve_and_save_councils(district)

        Methods to retrieve specifc static data.

    .. method:: retrieve_and_save_all

        Retrieves and saves all static data.

For dynamic data, and given the size of the database, the approach is more complex.

.. class:: Crawler

    A crawler for entities and contracts. This class has one public method, :meth:`update_all` that does
    all the heavy lifting. Here we explain in detail what it does.

    It requires the existence of two directories:

    .. attribute:: data_directory = '../../data'
    .. attribute:: contracts_directory = '../../contracts'

    .. warning:: These directories will be filled with millions of files,
        with total size of the order of 1.7 GB as of Jan. of 2013.

    .. method:: update_all()

        Updates the database with the latest entities and contracts by calling :meth:`update_entities` and
        :meth:`update_contracts`, respectively and in this order.
        All data retrieved from BASE is file-cached in :attr:`data_directory` and :attr:`contracts_directory`.

    Base_ exposes the list of contracts and entities using blocks of 25 elements.
    For entities, the blocks have all the required information, so, we
    save 25 entities per hit. For contracts, we need to go to the url
    of each contract of the block, so we need 26 hits (1+25).

    In both cases, the idea is the same: we start in the first block, and we retrieve blocks consecutively
    until a block returns no data. To minimize hitting Base_, the JSON content from a retrieved
    full block is cached in a file and subsequent calls use the cached data.

    To update contracts:

    .. method:: update_contracts()

        Updates the database by retrieving :class:`contracts <contracts.models.Contract>` from Base_.

        First, it hits Base_ database to retrieve 25 contracts :attr:`~contracts.models.Contract.base_id`,
        saving these on a file.
        Next, it hits the Base_ database for each contract in the block, saving these on a file.
        Finally, it creates a database entry (if it doesn't exist) for each :class:`contract <contracts.models.Contract>`
        on the block. This is repeated until a retrieved block returns no entries.

        Subsequent calls of this function start from the last block, avoiding further hits on Base_ database.

    To update entities:

    .. method:: update_entities()

        Updates the database by retrieving :class:`entities <contracts.models.Entity>` from Base_.

        Similar to :meth:`update_contracts` but for :class:`entities <contracts.models.Entity>`.
        It only hits Base_ database for getting the block of 25 entities because Base_ interface already provides
        the relevant information of the entity in the list.

        Like update_contracts, this method also saves the retrieved information in files.
