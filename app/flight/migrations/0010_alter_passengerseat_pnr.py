# Generated by Django 4.1 on 2023-11-24 09:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("flight", "0009_passenger_seatdistribution_seat_avail_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="passengerseat",
            name="pnr",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="flight.pnr"
            ),
        ),
    ]
