# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_field_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='criterion',
            name='ratio',
            field=models.FloatField(default=1.0, db_column='Ratio'),
        ),
    ]
