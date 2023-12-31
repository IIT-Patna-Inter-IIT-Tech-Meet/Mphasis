# Generated by Django 4.2.7 on 2023-12-01 19:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('flight', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classtype',
            name='lower',
        ),
        migrations.RemoveField(
            model_name='classtype',
            name='upper',
        ),
        migrations.AddField(
            model_name='flight',
            name='status',
            field=models.CharField(choices=[('Scheduled', 'Booking open'), ('Planning', 'Booking not allowed'), ('Canclled', 'Time to reschedule')], default='Scheduled', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='flight',
            name='schedule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='flight.flightscheduledate'),
        ),
    ]
