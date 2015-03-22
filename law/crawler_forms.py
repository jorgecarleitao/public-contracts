from django.forms import CharField, DateField, IntegerField, Form

from . import models


class TypeField(CharField):
    """
    Validates a relation to a ``models.Category``.
    """
    def clean(self, string):
        type_name = string.strip()

        # synonymous and typos check
        if type_name == 'Declaração de Rectificação':
            type_name = 'Declaração de Retificação'
        if type_name == 'Declaração de rectificação':
            type_name = 'Declaração de Retificação'
        if type_name == 'Decreto do Presidente de República':
            type_name = 'Decreto do Presidente da República'
        if type_name == 'Resolução da  Assembleia da República':
            type_name = 'Resolução da Assembleia da República'

        return type_name


class NumberField(CharField):
    """
    Some numbers contain more than they should.
    E.g. publication 638275, whose number is `'4/93, de 13 de Setembro'`
    """
    def clean(self, value):
        if value is not None and ',' in value:
            value = value.split(',')[0]
        if value is not None and ' - ' in value:
            value = value.split(' - ')[0]
        if value is not None and ' ' in value:
            value = value.split(' ')[0]

        return super(NumberField, self).clean(value)


class DocumentForm(Form):
    number = NumberField(required=False, max_length=20)

    creator_name = CharField()
    date = DateField()
    summary = CharField(required=False)
    text = CharField(required=False)
    dre_doc_id = IntegerField()
    dre_pdf_id = IntegerField()
    dr_series = CharField(max_length=10)
    dr_number = CharField(max_length=10)
    dr_supplement = CharField(required=False, max_length=50)
    dr_pages = CharField(max_length=50)

    type = TypeField()

    def clean_type(self):
        series = self.cleaned_data['dr_series']
        type, created = models.Type.objects.get_or_create(
            name=self.cleaned_data['type'], dr_series=series)
        return type
