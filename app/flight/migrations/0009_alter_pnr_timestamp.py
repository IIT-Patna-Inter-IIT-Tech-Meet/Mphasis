# Generated by Django 4.2.7 on 2023-11-27 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flight', '0008_pnr_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pnr',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
