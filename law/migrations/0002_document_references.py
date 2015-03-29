# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('law', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='references',
            field=models.ManyToManyField(to='law.Document'),
        ),
    ]
