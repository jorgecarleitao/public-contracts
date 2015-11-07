from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0003_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='entitydata',
            name='is_updated',
            field=models.BooleanField(default=False),
        ),
    ]
