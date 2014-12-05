# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deputy',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('official_id', models.IntegerField()),
                ('name', models.CharField(max_length=254)),
                ('birthday', models.DateField(null=True)),
                ('is_active', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Legislature',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField()),
                ('date_start', models.DateField()),
                ('date_end', models.DateField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Mandate',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('date_start', models.DateField()),
                ('date_end', models.DateField(null=True)),
                ('deputy', models.ForeignKey(to='deputies.Deputy')),
                ('district', models.ForeignKey(to='contracts.District', null=True)),
                ('legislature', models.ForeignKey(to='deputies.Legislature')),
            ],
            options={
                'ordering': ['-legislature__number'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Party',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('abbrev', models.CharField(max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='mandate',
            name='party',
            field=models.ForeignKey(to='deputies.Party'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='deputy',
            name='party',
            field=models.ForeignKey(to='deputies.Party', null=True),
            preserve_default=True,
        ),
    ]
