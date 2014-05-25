from django.forms import CharField, ModelChoiceField, IntegerField, Form

from . import models


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


class EntityForm(Form):
    """
    Validate data for a ``models.Entity``.
    """
    base_id = IntegerField()
    name = CharField()
    nif = CharField()
    country = CountryChoiceField(required=False)
