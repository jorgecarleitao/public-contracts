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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('number', models.CharField(max_length=20, null=True)),
                ('creator_name', models.TextField()),
                ('date', models.DateField()),
                ('summary', models.TextField(null=True)),
                ('text', models.TextField(null=True)),
                ('dre_doc_id', models.IntegerField(db_index=True, unique=True)),
                ('dre_pdf_id', models.IntegerField(db_index=True, unique=True)),
                ('dr_series', models.CharField(max_length=10, db_index=True)),
                ('dr_number', models.CharField(max_length=10)),
                ('dr_supplement', models.CharField(max_length=50, null=True)),
                ('dr_pages', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=254)),
                ('dr_series', models.CharField(max_length=10)),
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
        migrations.AlterUniqueTogether(
            name='type',
            unique_together=set([('name', 'dr_series')]),
        ),
    ]
