# Generated by Django 4.2.7 on 2023-12-13 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flight', '0006_alter_airport_ident'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='avilable_inventory',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]
