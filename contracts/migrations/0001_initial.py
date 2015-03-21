# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('base_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=254)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('lft', models.PositiveIntegerField(db_index=True)),
                ('rgt', models.PositiveIntegerField(db_index=True)),
                ('tree_id', models.PositiveIntegerField(db_index=True)),
                ('depth', models.PositiveIntegerField(db_index=True)),
                ('code', models.CharField(max_length=254)),
                ('description_en', models.CharField(max_length=254)),
                ('description_pt', models.CharField(max_length=254)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('base_id', models.IntegerField(unique=True)),
                ('added_date', models.DateField()),
                ('signing_date', models.DateField(null=True)),
                ('close_date', models.DateField(null=True)),
                ('description', models.TextField(null=True)),
                ('contract_description', models.TextField()),
                ('cpvs', models.CharField(max_length=254, null=True)),
                ('price', models.BigIntegerField()),
                ('category', models.ForeignKey(null=True, to='contracts.Category')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContractType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('base_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=254)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Council',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=254)),
                ('base_id', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=254)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=254)),
                ('base_id', models.IntegerField(unique=True)),
                ('country', models.ForeignKey(to='contracts.Country')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=254)),
                ('base_id', models.IntegerField(unique=True)),
                ('nif', models.CharField(max_length=254)),
                ('country', models.ForeignKey(null=True, to='contracts.Country')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityData',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('total_earned', models.BigIntegerField(default=0)),
                ('total_expended', models.BigIntegerField(default=0)),
                ('entity', models.OneToOneField(to='contracts.Entity', related_name='data')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ModelType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('base_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=254)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProcedureType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('base_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=254)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tender',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('base_id', models.IntegerField(unique=True)),
                ('description', models.TextField()),
                ('announcement_number', models.CharField(max_length=254)),
                ('publication_date', models.DateField()),
                ('deadline_date', models.DateField()),
                ('cpvs', models.CharField(max_length=254, null=True)),
                ('price', models.BigIntegerField()),
                ('dre_url', models.TextField()),
                ('act_type', models.ForeignKey(to='contracts.ActType')),
                ('category', models.ForeignKey(null=True, to='contracts.Category')),
                ('contract_type', models.ForeignKey(null=True, to='contracts.ContractType')),
                ('contractors', models.ManyToManyField(to='contracts.Entity')),
                ('model_type', models.ForeignKey(to='contracts.ModelType')),
            ],
            options={
                'ordering': ['-publication_date'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='council',
            name='district',
            field=models.ForeignKey(to='contracts.District'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contract',
            name='contract_type',
            field=models.ForeignKey(null=True, to='contracts.ContractType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contract',
            name='contracted',
            field=models.ManyToManyField(to='contracts.Entity'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contract',
            name='contractors',
            field=models.ManyToManyField(to='contracts.Entity', related_name='contracts_made'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contract',
            name='council',
            field=models.ForeignKey(null=True, to='contracts.Council'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contract',
            name='country',
            field=models.ForeignKey(null=True, to='contracts.Country'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contract',
            name='district',
            field=models.ForeignKey(null=True, to='contracts.District'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contract',
            name='procedure_type',
            field=models.ForeignKey(null=True, to='contracts.ProcedureType'),
            preserve_default=True,
        ),
    ]
