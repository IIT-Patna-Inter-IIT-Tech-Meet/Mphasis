# Generated by Django 4.1 on 2023-11-24 15:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("flight", "0012_remove_aircraft_cabin_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flight",
            name="aircraft_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING, to="flight.aircraft"
            ),
        ),
        migrations.AlterField(
            model_name="flight",
            name="arrival_airport_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="arrival_airport",
                to="flight.airport",
            ),
        ),
        migrations.AlterField(
            model_name="flight",
            name="departure_airport_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="departure_airport",
                to="flight.airport",
            ),
        ),
        migrations.AlterField(
            model_name="passengerseat",
            name="passenger",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING, to="flight.passenger"
            ),
        ),
        migrations.AlterField(
            model_name="passengerseat",
            name="seat_cabin",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING, to="flight.cabintype"
            ),
        ),
        migrations.AlterField(
            model_name="passengerseat",
            name="seat_class",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING, to="flight.classtype"
            ),
        ),
        migrations.AlterField(
            model_name="seatdistribution",
            name="aircraft_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING, to="flight.aircraft"
            ),
        ),
        migrations.AlterField(
            model_name="seatdistribution",
            name="cabin_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING, to="flight.cabintype"
            ),
        ),
        migrations.AlterField(
            model_name="seatdistribution",
            name="class_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING, to="flight.classtype"
            ),
        ),
    ]
