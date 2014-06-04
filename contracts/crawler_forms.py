from datetime import timedelta
import re

from django.core.exceptions import ValidationError
from django.forms import CharField, \
    DateField, ModelChoiceField, IntegerField,\
    Field, ModelMultipleChoiceField, Form

from . import models


def clean_place(value):
    """
    value='Portugal, Faro, Castro Marim<BR/>Portugal'
    returns 'Portugal', 'Faro', 'Castro Marim',

    value='Portugal, Faro<BR/>Portugal'
    returns 'Portugal', 'Faro'
    """
    names = re.split(', |<BR/>', value)
    while len(names) < 3:
        names.append(None)
    return tuple(names)


class PriceField(IntegerField):
    """
    Validates BASE prices
    """
    def clean(self, value):
        value = value.split(' ')[0]
        value = value.replace(".", "").replace(",", "")
        return super(PriceField, self).clean(value)


class TimeDeltaField(Field):
    """
    Validates a timedelta of the form "%d dias.".
    """
    def clean(self, value):
        if ' ' in value:
            strings = value.split(' ')
            if strings[1] == 'dias.':
                return timedelta(days=int(strings[0]))

        return timedelta()


class CPVSField(CharField):
    """
    Validates BASE cpvs.
    """
    def clean(self, value):
        value = super(CPVSField, self).clean(value)
        if value is None:
            return None

        expression = re.compile("(\d{8}-\d),.*")
        match = expression.match(value)

        if match:
            return match.group(1)
        else:
            return None


class EntitiesField(ModelMultipleChoiceField):
    """
    Validates multiple entities based on BASE data.
    """
    def __init__(self, **kwargs):
        super(EntitiesField, self).__init__(queryset=models.Entity.objects,
                                            to_field_name='base_id', **kwargs)

    def clean(self, value):
        value = [item['id'] for item in value]

        try:
            return super(EntitiesField, self).clean(value)
        except ValidationError:
            # in case we don't have the entity, we try to retrieve it from BASE.
            import contracts.crawler
            entity_crawler = contracts.crawler.EntitiesCrawler()

            for base_id in value:
                entity_crawler.update_instance(base_id)

            return super(EntitiesField, self).clean(value)


class CountryChoiceField(ModelChoiceField):
    """
    Validates a relation to a ``models.Country``.
    """
    def __init__(self, **kwargs):
        super(CountryChoiceField, self).__init__(queryset=models.Country.objects,
                                                 to_field_name='name', **kwargs)

    def clean(self, value):
        if value == 'Não definido.':
            value = None
        return super(CountryChoiceField, self).clean(value)


class CouncilChoiceField(Field):
    """
    Validates a relation to a ``models.Council``.
    """
    def clean(self, value):
        if value['council'] is None:
            return None
        district = value['district']
        council = value['council']

        return models.Council.objects.get(name=council, district__name=district)


class CategoryField(ModelChoiceField):
    """
    Validates a relation to a ``models.Category``.
    """
    def __init__(self, **kwargs):
        super(CategoryField, self).__init__(queryset=models.Category.objects,
                                            to_field_name='code', **kwargs)

    def clean(self, value):
        if value == 'Não definido.':
            value = None

        cpvs = CPVSField(required=self.required).clean(value)
        try:
            return super(CategoryField, self).clean(cpvs)
        except ValidationError:
            return None


class ContractTypeField(ModelChoiceField):
    """
    Validates a relation to a ``models.ContractType``.
    """
    def __init__(self, **kwargs):
        super(ContractTypeField, self).__init__(queryset=models.ContractType.objects,
                                                to_field_name='name', **kwargs)

    def clean(self, value):
        if value == 'Outros Tipos (Não Preenchido)' or value == 'Não definido.':
            return None
        ## sometimes it has more than one type (~1 in 100.000); we only consider the first.
        if '<br/>' in value:
            value = value.split('<br/>')[0]
        elif '; ' in value:
            value = value.split('; ')[0]

        return super(ContractTypeField, self).clean(value)


class DREDocument(CharField):
    """
    The integer value of the last argument of the url
    """
    def clean(self, value):
        return int(value.split('=')[-1])


class EntityForm(Form):
    """
    Validate data for a ``models.Entity``.
    """
    base_id = IntegerField()
    name = CharField()
    nif = CharField()
    country = CountryChoiceField(required=False)


class ContractForm(Form):
    """
    Validate data for a ``models.Contract``.
    """
    base_id = IntegerField()

    description = CharField(required=False)
    price = PriceField(required=False)
    contract_description = CharField(required=False)
    added_date = DateField(input_formats=["%d-%m-%Y"])
    signing_date = DateField(input_formats=["%d-%m-%Y"], required=False)

    cpvs = CPVSField(required=False)
    category = CategoryField(required=False)
    procedure_type = ModelChoiceField(queryset=models.ProcedureType.objects, to_field_name='name', required=False)
    contract_type = ContractTypeField(required=False)

    contractors = EntitiesField()
    contracted = EntitiesField()

    country = ModelChoiceField(queryset=models.Country.objects, to_field_name='name', required=False)
    district = ModelChoiceField(queryset=models.District.objects, to_field_name='name', required=False)
    council = CouncilChoiceField(required=False)


class TenderForm(Form):
    base_id = IntegerField()

    description = CharField(required=False)
    price = PriceField(required=False)
    publication_date = DateField(input_formats=["%d-%m-%Y"])
    deadline_date = TimeDeltaField(required=False)

    cpvs = CPVSField(required=False)
    category = CategoryField(required=False)

    act_type = ModelChoiceField(queryset=models.ActType.objects, to_field_name='name', required=False)
    model_type = ModelChoiceField(queryset=models.ModelType.objects, to_field_name='name', required=False)
    contract_type = ContractTypeField(required=False)

    announcement_number = CharField(required=False)

    contractors = EntitiesField()

    dre_document = DREDocument()
    dre_number = CharField()
    dre_series = CharField()

    def clean_deadline_date(self):
        deadline_date = self.cleaned_data['publication_date']
        deadline_date += self.cleaned_data['deadline_date']

        return deadline_date
