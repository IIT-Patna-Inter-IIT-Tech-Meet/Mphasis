# Generated by Django 4.1 on 2023-11-26 11:52

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Aircraft",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("model", models.CharField(max_length=25)),
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                ("registration", models.CharField(max_length=255)),
                ("owner_code", models.CharField(max_length=255)),
                ("owner_name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Airport",
            fields=[
                (
                    "id",
                    models.IntegerField(primary_key=True, serialize=False, unique=True),
                ),
                ("ident", models.CharField(max_length=4)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("large_airport", "Large Airport"),
                            ("medium_airport", "Medium Airport"),
                            ("small_airport", "Small Airport"),
                            ("heliport", "Heliport"),
                            ("closed", "Closed"),
                            ("seaplane_base", "Seaplane Base"),
                            ("balloonport", "Balloonport"),
                        ],
                        max_length=255,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("latitude_deg", models.FloatField()),
                ("longitude_deg", models.FloatField()),
                ("elevation_ft", models.IntegerField(blank=True, null=True)),
                ("continent", models.CharField(max_length=2, null=True)),
                ("continent_name", models.CharField(max_length=255, null=True)),
                ("iso_country", models.CharField(max_length=2)),
                ("iso_region", models.CharField(max_length=7)),
                ("local_region", models.CharField(max_length=255, null=True)),
                ("municipality", models.CharField(max_length=255, null=True)),
                ("scheduled_service", models.BooleanField()),
                ("gps_code", models.CharField(max_length=4, null=True)),
                ("iata_code", models.CharField(max_length=3, null=True)),
                ("local_code", models.CharField(max_length=4, null=True)),
                ("home_link", models.URLField(null=True)),
                ("wikipedia_link", models.URLField(null=True)),
                ("keywords", models.CharField(max_length=255, null=True)),
                ("score", models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="CabinType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("type_name", models.CharField(max_length=255)),
                ("des", models.CharField(max_length=225)),
                ("score", models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="ClassType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("type_name", models.CharField(max_length=255)),
                ("des", models.CharField(max_length=225)),
                ("score", models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="Group",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("group_name", models.CharField(max_length=255)),
                ("group_des", models.CharField(max_length=255)),
                ("group_point", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Passenger",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                (
                    "phone_no",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=128, region=None
                    ),
                ),
                ("email", models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name="SSR",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("ssr_name", models.CharField(max_length=255)),
                ("ssr_des", models.CharField(max_length=255)),
                ("srr_point", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="SeatDistribution",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("seat_count", models.IntegerField(default=0)),
                ("seat_avail", models.IntegerField(default=0)),
                (
                    "aircraft_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="flight.aircraft",
                    ),
                ),
                (
                    "cabin_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="flight.cabintype",
                    ),
                ),
                (
                    "class_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="flight.classtype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PNR",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("timestamp", models.DateTimeField()),
                ("total_amount", models.FloatField(default=0)),
                ("total_tax", models.FloatField(default=0)),
                ("total_price", models.FloatField(default=0)),
                ("seat_currency", models.CharField(max_length=255)),
                ("paid_service", models.BooleanField(default=False)),
                ("loyalty_program", models.BooleanField(default=False)),
                ("conn", models.IntegerField(default=0)),
                ("pax", models.ImageField(default=0, upload_to="")),
                (
                    "passenger",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="flight.passenger",
                    ),
                ),
                (
                    "seat_cabin",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="flight.cabintype",
                    ),
                ),
                (
                    "seat_class",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="flight.classtype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PassengerSSR",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                (
                    "pnr",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="flight.pnr"
                    ),
                ),
                (
                    "ssr",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING, to="flight.ssr"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PassengerSeat",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                (
                    "passenger",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="flight.passenger",
                    ),
                ),
                (
                    "pnr",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="flight.pnr"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PassengerGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="flight.group",
                    ),
                ),
                (
                    "pnr",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="flight.pnr"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Flight",
            fields=[
                (
                    "id",
                    models.CharField(
                        max_length=255, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("flight_number", models.CharField(max_length=255)),
                ("departure_time", models.DateTimeField()),
                ("arrival_time", models.DateTimeField()),
                ("flight_time", models.IntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("green", "landed and open for entry"),
                            ("red", "landed and no entry"),
                            ("grey", "scheduled"),
                        ],
                        max_length=255,
                    ),
                ),
                (
                    "aircraft_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="flight.aircraft",
                    ),
                ),
                (
                    "arrival_airport_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="arrival_airport",
                        to="flight.airport",
                    ),
                ),
                (
                    "departure_airport_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="departure_airport",
                        to="flight.airport",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ConnectingFlight",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                (
                    "flight",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="flight.flight",
                    ),
                ),
                (
                    "pnr",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="flight.pnr"
                    ),
                ),
            ],
        ),
    ]
