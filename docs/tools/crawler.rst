Crawler for Contracts and Tenders
=================================

.. currentmodule:: contracts.crawler

.. _Base: http://www.base.gov.pt/base2
.. _mechanize: http://wwwsearch.sourceforge.net/mechanize/

This document explains how Base_ provides its data and what our crawler works.

.. important::
    Please, take precautions on using the crawler on your own as it can generate Denial of
    Service (DoS) to Base_ database. We provide remote access to ours exactly to avoid that.

.. important::
    Crawling the Base_ from scratch can take more than 2 days as of Jan. 2014.

Base database
-------------

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
---------------------

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

    An object able to retrieve content from an url. When initialized, it initializes a mechanize_ browser.
    It has one method:

    .. method:: goToPage(url)

        Returns the html of the url.

.. class::JSONCrawler

    A subclass of AbstractCrawler able to retrieve JSON content from an url.
    It has one method:

    .. method:: goToPage(url)

        Returns a dictionary corresponding to the json content of the url.

For retrieving data, the procedure is separated in three steps:

1. Go to the url and retrieve the data
2. Validate the data
3. Populate the database with the validated data.

For static data, this is relatively easy. We provide a specific crawler for this:

.. class:: ContractsStaticDataCrawler

    A subclass JSONCrawler for static data of contracts. This crawler only needs to be run once and
    is used to populate the database the first time.

    .. method:: retrieve_and_save_contracts_types()
    .. method:: retrieve_and_save_procedures_types()
    .. method:: retrieve_and_save_countries()
    .. method:: retrieve_and_save_districts(country)
    .. method:: retrieve_and_save_councils(district)

        Methods to retrieve specific static data.

    .. method:: retrieve_and_save_all

        Retrieves and saves all static data of contracts.


.. class:: TendersStaticDataCrawler

    A subclass JSONCrawler for static data of tenders. This crawler only needs to be run once and
    is used to populate the database the first time.

    .. method:: retrieve_and_save_act_types()
    .. method:: retrieve_and_save_model_types()

        Methods to retrieve specific static data.

    .. method:: retrieve_and_save_all()

        Retrieves and saves all static data of tenders.

.. class:: StaticDataCrawler

    A crawler that uses composite design pattern to just extract all static date (tenders and contracts).

    .. method:: retrieve_and_save_all()

        Retrieves and saves all static data.

For dynamic data, and given the size of the database, the approach is more complex.

.. class:: DynamicCrawler

    A subclass JSONCrawler (abstract) that conceptually uses a directory to store files with lists of 25 summaries.

    .. attribute:: data_directory = '../../data'


.. class:: EntitiesCrawler

    A subclass of DynamicCrawler to crawl entities.

    It goes to all lists of entities in Base_, each with 25 elements, and store them in files in :attr:`data_directory`.
    Uses the stored pages to create/update :class:`Entities <models.Entity>` in the database.

    .. method:: update()

        The entry point of this crawler; given the existence of :attr:`data_directory`,
        updates :class:`Entities <models.Entity>` until database is fully synchronized with Base_.


.. class:: ContractsCrawler

    A subclass of DynamicCrawler to crawl contracts.

    It goes to all lists of entities in Base_, each with 25 elements, and store the ids in files in :attr:`data_directory`.

    Goes to the page of each :class:`models.Contract`, obtained from the stored ids, and stores the information in

    .. attribute:: contracts_directory = '../../contracts'

        directory of cached information of contracts.

    .. warning:: This directory will be filled with lots of files,
        with total size of ~1.7 GB as of Jan. of 2014.

    .. method:: update()

        Entry point of this crawler, given the existence of :attr:`contracts_directory` and :attr:`data_directory`,
        downloads, caches and saves contracts until the database is fully synchronized with Base_.


.. class:: TenderCrawler

    A subclass of DynamicCrawler to crawl tenders.

    It sequentially searches for tenders with a given id, retrieves it, and caches the results in

    .. attribute:: tenders_directory = '../../tenders'

    Used to synchronized tenders with Base_.

    .. method:: update()

        Entry point of this crawler, given the existence of :attr:`tenders_directory` and :attr:`data_directory`,
        downloads, caches and saves :class:`tenders <models.Tender>` until the database is fully synchronized with Base_.
