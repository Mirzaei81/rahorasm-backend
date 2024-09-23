# Generated by Django 5.1 on 2024-09-23 08:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TourManager', '0004_continent_alter_airline_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cities', to='TourManager.country'),
        ),
        migrations.AlterField(
            model_name='country',
            name='continent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='countries', to='TourManager.continent'),
        ),
    ]
