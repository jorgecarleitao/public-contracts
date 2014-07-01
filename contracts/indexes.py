from sphinxql import indexes, fields
from .models import Entity


class EntityIndex(indexes.Index):
    name = fields.Text('name')

    class Meta:
        model = Entity


# class ContractIndex(indexes.Index):
#     name = fields.Text('description')
#     description = fields.Text('contract_description')
#
#     class Meta:
#         model = Contract
