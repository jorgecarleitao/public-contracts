from django.db.models import Value, F, TextField
from django.db.models.functions import Concat

from sphinxql import indexes, fields
from .models import Document


class DocumentIndex(indexes.Index):
    name = fields.Text(Concat(F('type__name'), Value(' '), F('number'),
                              output_field=TextField()))
    summary = fields.Text('summary')
    text = fields.Text('text')

    class Meta:
        model = Document
        range_step = 10000
