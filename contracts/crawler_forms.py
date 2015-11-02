import datetime
from datetime import timedelta
import re

from django.core.exceptions import ValidationError
from django.db import transaction
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
    places = re.split('<BR/>', value)  # different locations

    # split each in (country, district, council)
    places = [re.split(', ', place) for place in places]
    place = places[0]
    # remove locations not determined
    place = [location for location in place if 'não determinado' not in location]

    # fill place with Nones if incomplete
    while len(place) < 3:
        place.append(None)
    return tuple(place)


class PriceField(IntegerField):
    """
    Validates BASE prices
    """
    def clean(self, value):
        value = value.split(' ')[0]
        value = value.replace(".", "").replace(",", "")
        return super().clean(value)


class TimeDeltaField(CharField):
    """
    Validates a timedelta of the form "%d dias.".
    """
    re = re.compile('(\d+) dias\.')

    def clean(self, value):
        super(TimeDeltaField, self).clean(value)

        result = self.re.search(value)
        if not result:
            raise ValidationError('Validation of "%s" failed' % value)

        return timedelta(days=int(result.group(1)))


class CPVSField(CharField):
    """
    Validates BASE cpvs.
    """
    def clean(self, value):
        value = super(CPVSField, self).clean(value)
        if value in ('', 'Não definido.'):
            return None

        expression = re.compile("(\d{8}-\d)")
        match = expression.match(value)

        if match:
            return match.group(1)
        else:
            raise ValidationError('CPV "%s" not correct', value)


class EntitiesField(ModelMultipleChoiceField):
    """
    Validates multiple entities based on BASE data.
    """
    def __init__(self, **kwargs):
        super().__init__(queryset=models.Entity.objects,
                         to_field_name='base_id', **kwargs)

    def clean(self, value):
        value = [item['id'] for item in value]

        try:
            return super().clean(value)
        except ValidationError:
            # in case we don't have the entity, we try to retrieve it from BASE.
            import contracts.crawler
            entity_crawler = contracts.crawler.EntitiesCrawler()

            try:
                with transaction.atomic():
                    for base_id in value:
                        entity_crawler.update_instance(base_id)
            except (contracts.crawler.JSONLoadError, ValidationError):
                raise ValidationError("An entity in %s doesn't exist in BASE." %
                                      value)

            return super().clean(value)


class CountryChoiceField(ModelChoiceField):
    """
    Validates a relation to a ``models.Country``.
    """
    def __init__(self, **kwargs):
        super().__init__(queryset=models.Country.objects,
                         to_field_name='name', **kwargs)

    def clean(self, value):
        if value == 'Não definido.':
            value = None
        return super().clean(value)


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
        super().__init__(queryset=models.Category.objects,
                         to_field_name='code', **kwargs)

    def clean(self, value):
        if value == 'Não definido.':
            value = None

        cpvs = CPVSField(required=self.required).clean(value)
        try:
            return super().clean(cpvs)
        except ValidationError:
            return None


class ContractTypeField(ModelChoiceField):
    """
    Validates a relation to a ``models.ContractType``.
    """
    def __init__(self, **kwargs):
        super().__init__(queryset=models.ContractType.objects,
                         to_field_name='name', **kwargs)

    def clean(self, value):
        if value == 'Não definido.':
            return None
        # sometimes it has more than one type (~1 in 100.000);
        # we only consider the first.
        if '<br/>' in value:
            value = value.split('<br/>')[0]
        elif '; ' in value:
            value = value.split('; ')[0]

        if value.startswith('Outros'):
            value = 'Outros'

        return super().clean(value)


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
    procedure_type = ModelChoiceField(queryset=models.ProcedureType.objects,
                                      to_field_name='name', required=False)
    contract_type = ContractTypeField(required=False)

    contractors = EntitiesField()
    contracted = EntitiesField()

    country = ModelChoiceField(queryset=models.Country.objects,
                               to_field_name='name', required=False)
    district = ModelChoiceField(queryset=models.District.objects,
                                to_field_name='name', required=False)
    council = CouncilChoiceField(required=False)


class TenderForm(Form):
    base_id = IntegerField()

    description = CharField(required=False)
    price = PriceField(required=False)
    publication_date = DateField(input_formats=["%d-%m-%Y"])
    deadline_date = TimeDeltaField(required=False)

    cpvs = CPVSField(required=False)
    category = CategoryField(required=False)

    act_type = ModelChoiceField(queryset=models.ActType.objects,
                                to_field_name='name', required=False)
    model_type = ModelChoiceField(queryset=models.ModelType.objects,
                                  to_field_name='name', required=False)
    contract_type = ContractTypeField(required=False)

    announcement_number = CharField(required=False)

    contractors = EntitiesField()

    dre_url = CharField()

    @staticmethod
    def prepare_publication_date(data):
        """
        When publication_date is not available, we try to get it from the URL.
        """
        if not data['publication_date']:
            try:
                x = re.findall(r'&data=(\d+)\-(\d+)\-(\d+)&',
                               data['dre_url'])[0]
            except IndexError:
                return None

            date = datetime.date(year=int(x[0]), month=int(x[1]), day=int(x[2]))
            return date
        else:
            return data['publication_date']

    def clean_deadline_date(self):
        """
        Deadline requires knowledge of publication date.
        """
        if 'publication_date' in self.cleaned_data:
            deadline_date = self.cleaned_data['publication_date']
            deadline_date += self.cleaned_data['deadline_date']

            return deadline_date
        # else validation will fail because publication_date is required.
