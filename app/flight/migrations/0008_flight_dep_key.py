# Generated by Django 4.2.7 on 2023-12-14 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flight', '0007_flight_avilable_inventory'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='dep_key',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]
