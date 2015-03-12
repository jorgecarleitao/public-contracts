[![Build Status](https://travis-ci.org/jorgecarleitao/public-contracts.svg)](https://travis-ci.org/jorgecarleitao/public-contracts)

# Publics pt

Publics pt is an open source Django website and API to query and analyse data of
the portuguese state. Thanks for checking it out.

## The problem we aim to solve

This website aims to:

1. Provide a consistent way to query portuguese public data using Django ORM
2. Interrelate different public data
3. Extract and present statistical features of the data

and consists in 4 components:

1. A set of crawlers and validators that retrieve information from official databases and store them in Django models
2. A set of Django models (in Django Apps) to store the data in a database
3. A database with read access to anyone so anyone can query it by git-cloning this code.
4. A [website](http://publicos.pt) that uses the above points to provide some statistical features of the databases

## Scope

We focus on three aspects of the portuguese state:

1. Public Contracts: **contracts** between **entities** with a **value** and other fields.
2. Members of the Parliament: **Persons** that have **mandates** in **legislatures** of the parliament.
3. Laws: **documents** that are officially published as laws.

## The code

We use [Django](https://www.djangoproject.com/) ORM for the API and database
and d3.js for visualisations of statistical quantities of the database.
The official website is written in English and translated to portuguese (via i18n), also hosted here.

The code is licenced under BSD.

## Documentation

The API and the crawler are [documented](http://public-contracts.readthedocs.org/en/latest/).

## Pre-requisites and installation

The installation depend on what you want to do:

### To access and query the database 

1- Install Django, psycopg2, [django-treebeard](https://github.com/tabo/django-treebeard) and BeautifulSoup4:

`pip install -r api_requirements.txt` 

2- Download the source

`git clone git@github.com:jorgecarleitao/public-contracts.git`

3- Enter in the project's directory: 

`cd public-contracts`

4- Run the example:

`python -m contracts.tools.example`

you should see two numbers. You now have full access to the database.

### To deploy the website locally

1- Additionally to the installation above, install django-debug-toolbar and 
[Django-SphinxQL](https://github.com/jorgecarleitao/django-sphinxql):

`pip install -r website_requirements.txt`

2- Start the server:

`python manage.py runserver`

3- Enter in the url `127.0.0.1:8000`.

If something went wrong, please report an [issue](https://github.com/jorgecarleitao/public-contracts/issues)
so we can help you and improve these instructions.
