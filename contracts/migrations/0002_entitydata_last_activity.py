# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='entitydata',
            name='last_activity',
            field=models.DateField(db_index=True, default=None, null=True),
        ),
    ]
