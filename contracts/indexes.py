from sphinxql import indexes, fields
from .models import Entity, Contract, Tender


class EntityIndex(indexes.Index):
    name = fields.Text('name')

    class Meta:
        model = Entity


class ContractIndex(indexes.Index):
    name = fields.Text('description')
    description = fields.Text('contract_description')

    signing_date = fields.Date('signing_date')

    category_id = fields.Integer('category')

    category = fields.Text('category__description_pt')

    district = fields.Text('district__name')
    council = fields.Text('council__name')

    class Meta:
        model = Contract
        query = Contract.default_objects.all()


class TenderIndex(indexes.Index):
    description = fields.Text('description')

    category = fields.Text('category__description_pt')

    publication_date = fields.Date('publication_date')

    class Meta:
        model = Tender
