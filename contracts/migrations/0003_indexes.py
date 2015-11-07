from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0002_entitydata_last_activity'),
    ]

    operations = [
        # index NIF, that is used for searches
        migrations.RunSQL(
            'CREATE INDEX contracts_entity_nif_seq '
            'ON contracts_entity (nif)',
            reverse_sql='DROP INDEX contracts_entity_nif_seq;'),

        # price, we use it a lot for different things
        migrations.RunSQL(
            'CREATE INDEX contracts_contract_price_seq '
            'ON contracts_contract (price)',
            reverse_sql='DROP INDEX contracts_contract_price_seq'),

        # signing date, for ordering and select ranges
        migrations.RunSQL(
            'CREATE INDEX contracts_contract_signing_date_seq '
            'ON contracts_contract (signing_date)',
            reverse_sql='DROP INDEX contracts_contract_signing_date_seq'),
    ]
