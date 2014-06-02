# Publics pt

Publics pt is an open source Django website and API to query and analyse data of the portuguese state.
Thanks for checking it out.

## The problem we aim to solve

The portuguese state does not provide a consistent way to query public data, nor relating this data.
This website aims to:

1. Provide a consistent way to query portuguese public data using Django ORM
2. Interrelate different public data
3. Extract and present statistical features of the data

This project consists of 4 components:

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

1- Install Django and bindings to mysql.

`pip install django`

`pip install mysql-python` 

2- Install [django-treebeard](https://github.com/tabo/django-treebeard), a dependency.

`pip install django-treebeard`

3- Download the source

`git clone git@github.com:jorgecarleitao/public-contracts.git`

Enter in the directory `cd public-contracts/contracts`.

4- Run the example:

`python -m tools.example`

you should see two numbers.

If something went wrong, please report an [issue](https://github.com/jorgecarleitao/public-contracts/issues)
so we can improve these instructions.
