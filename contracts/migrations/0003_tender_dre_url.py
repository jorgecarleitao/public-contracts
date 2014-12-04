# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def write_dre_url(apps, schema_editor):
    Tender = apps.get_model("contracts", "Tender")
    for tender in Tender.objects.all():
        tender.dre_url = 'http://dre.pt/util/getpdf.asp?' \
                         's=udrcp&iddip=%d' % tender.dre_document
        tender.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0002_tender_description_to_textfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='tender',
            name='dre_url',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.RunPython(write_dre_url),
        migrations.RemoveField(
            model_name='tender',
            name='dre_document',
        ),
        migrations.RemoveField(
            model_name='tender',
            name='dre_number',
        ),
        migrations.RemoveField(
            model_name='tender',
            name='dre_series',
        ),
    ]
