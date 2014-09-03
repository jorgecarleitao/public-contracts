# these first two lines are used to setup a minimal Django environment
from main.tools import set_up
set_up.set_up_django_environment('main.settings_for_script')
# From this point on, we are ready to use Django for accessing the remote database.

from contracts import models
from django.db.models import Sum

# this query asks for all contracts in the database
all_contracts = models.Contract.objects.all()

# this query counts the previous query
number_of_contracts = all_contracts.count()
print(number_of_contracts)

# this query sums the prices of all contracts.
total_price = all_contracts.aggregate(sum=Sum('price'))['sum']
print(total_price)
