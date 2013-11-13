import set_up
set_up.set_up_django_environment()
from contracts import models

all_contracts = models.Contract.objects.all()

number_of_contracts = all_contracts.count()

print number_of_contracts

from django.db.models import Sum

total_price = all_contracts.aggregate(sum=Sum('price'))['sum']
print total_price
