# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Creator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=254, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('date', models.DateField()),
                ('number', models.CharField(null=True, max_length=20)),
                ('summary', models.TextField()),
                ('text', models.TextField(null=True)),
                ('dre_doc_id', models.IntegerField(db_index=True, unique=True)),
                ('pdf_url', models.CharField(max_length=200)),
                ('series', models.IntegerField(db_index=True)),
                ('series_number', models.CharField(max_length=10)),
                ('series_other', models.CharField(max_length=30, blank=True)),
                ('series_pages', models.CharField(max_length=50)),
                ('creator', models.ForeignKey(null=True, to='law.Creator')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=254, unique=True)),
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
