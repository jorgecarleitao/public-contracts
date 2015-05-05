from django.forms import CharField, DateField, IntegerField, Form

from . import models


class TypeField(CharField):
    """
    Validates a relation to a ``models.Type``.
    """
    mapping = {'Declaração de Rectificação': 'Declaração de Retificação',
               'Declaração de rectificação': 'Declaração de Retificação',
               'Decreto do Presidente de República':
                   'Decreto do Presidente da República',
               'Resolução da  Assembleia da República':
                   'Resolução da Assembleia da República'}

    def clean(self, string):
        type_name = string.strip()

        # synonymous and typos check
        if type_name in self.mapping:
            type_name = self.mapping[type_name]

        return type_name


class DocumentForm(Form):
    number = CharField(required=False, max_length=20)

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
        if 'dr_series' not in self.cleaned_data or 'type' not in self.cleaned_data:
            return
        series = self.cleaned_data['dr_series']
        type, created = models.Type.objects.get_or_create(
            name=self.cleaned_data['type'], dr_series=series)
        return type
