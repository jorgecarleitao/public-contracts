# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('number', models.CharField(max_length=20, null=True)),
                ('creator_name', models.CharField(max_length=254)),
                ('date', models.DateField()),
                ('summary', models.TextField()),
                ('text', models.TextField()),
                ('dre_doc_id', models.IntegerField(unique=True, db_index=True)),
                ('dre_pdf_id', models.IntegerField(unique=True, db_index=True)),
                ('dr_series', models.CharField(db_index=True, max_length=10)),
                ('dr_number', models.CharField(max_length=10)),
                ('dr_supplement', models.CharField(max_length=30, null=True)),
                ('dr_pages', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=254)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='document',
            name='type',
            field=models.ForeignKey(to='law.Type'),
            preserve_default=True,
        ),
    ]
