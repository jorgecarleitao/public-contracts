Asking questions to the database
==================================

Once you :doc:`install <installation>` the database binder, you can directly start using it.
The installation already has the credentials to access :doc:`our database <tools/database>`.

Here we reproduce the what you can find in 'tools/example.py'.

Import the models using::

    from contracts import models

with this, you have just gained a piece of intellectual freedom:

what are the contracts?::

    all_contracts = models.Contract.objects.all()

how many they are?::

    number_of_contracts = all_contracts.count()

how much is their price?::

    from django.db.models import Sum

    total_price = all_contracts.aggregate(sum=Sum('price'))['sum']
    print total_price

from here on, the boundaries are just limited by those of your imagination...
