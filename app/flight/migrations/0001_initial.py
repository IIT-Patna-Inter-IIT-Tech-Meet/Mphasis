# Generated by Django 4.2.7 on 2023-12-01 14:39

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Aircraft',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, unique=True)),
                ('model', models.CharField(max_length=25)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('registration', models.CharField(max_length=255)),
                ('owner_code', models.CharField(max_length=255)),
                ('owner_name', models.CharField(max_length=255)),
                ('total_capacity', models.IntegerField(default=0)),
                ('total_invenotry', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('ident', models.CharField(max_length=4)),
                ('type', models.CharField(choices=[('large_airport', 'Large Airport'), ('medium_airport', 'Medium Airport'), ('small_airport', 'Small Airport'), ('heliport', 'Heliport'), ('closed', 'Closed'), ('seaplane_base', 'Seaplane Base'), ('balloonport', 'Balloonport')], max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('latitude_deg', models.FloatField()),
                ('longitude_deg', models.FloatField()),
                ('elevation_ft', models.IntegerField(blank=True, null=True)),
                ('continent', models.CharField(max_length=2, null=True)),
                ('continent_name', models.CharField(max_length=255, null=True)),
                ('iso_country', models.CharField(max_length=2)),
                ('iso_region', models.CharField(max_length=7)),
                ('local_region', models.CharField(max_length=255, null=True)),
                ('municipality', models.CharField(max_length=255, null=True)),
                ('scheduled_service', models.BooleanField()),
                ('gps_code', models.CharField(max_length=4, null=True)),
                ('iata_code', models.CharField(max_length=3, null=True)),
                ('local_code', models.CharField(max_length=4, null=True)),
                ('home_link', models.URLField(null=True)),
                ('wikipedia_link', models.URLField(null=True)),
                ('keywords', models.CharField(max_length=255, null=True)),
                ('score', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CabinType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('type_name', models.CharField(max_length=255)),
                ('des', models.CharField(max_length=225)),
                ('score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Carrier',
            fields=[
                ('code', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('desc', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ClassType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('type_name', models.CharField(max_length=255)),
                ('des', models.CharField(max_length=225)),
                ('score', models.IntegerField(default=0)),
                ('upper', models.IntegerField(default=0)),
                ('lower', models.IntegerField(default=0)),
                ('cabin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='flight.cabintype')),
            ],
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('flight_id', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='FlightSchedule',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('departure_time', models.TimeField(null=True)),
                ('arrival_time', models.TimeField()),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('r_sun', models.BooleanField(default=False)),
                ('r_mon', models.BooleanField(default=False)),
                ('r_tue', models.BooleanField(default=False)),
                ('r_wed', models.BooleanField(default=False)),
                ('r_thr', models.BooleanField(default=False)),
                ('r_fri', models.BooleanField(default=False)),
                ('r_sat', models.BooleanField(default=False)),
                ('freq', models.IntegerField(default=0)),
                ('dept_count', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('Scheduled', 'Booking open'), ('Planning', 'Booking not allowed'), ('Canclled', 'Time to reschedule')], max_length=255)),
                ('aircraft_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='flight.aircraft')),
                ('arrival_airport', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='arrival_airport', to='flight.airport')),
                ('carrier_cd', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='flight.carrier')),
                ('departure_airport', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='departure_airport', to='flight.airport')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('group_name', models.CharField(max_length=255)),
                ('group_des', models.CharField(max_length=255)),
                ('group_point', models.IntegerField()),
                ('probability', models.FloatField(default=0.2)),
            ],
        ),
        migrations.CreateModel(
            name='PNR',
            fields=[
                ('pnr', models.CharField(max_length=6, primary_key=True, serialize=False, unique=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('dep_key', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=10)),
                ('seg_seq', models.IntegerField(default=0)),
                ('carrier_cd', models.CharField(blank=True, max_length=5, null=True)),
                ('paid_service', models.BooleanField(default=False)),
                ('loyalty_program', models.BooleanField(default=False)),
                ('conn', models.IntegerField(default=0)),
                ('pax', models.IntegerField(default=0)),
                ('score', models.IntegerField(default=0)),
                ('booking_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='flight.group')),
                ('seat_class', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='flight.classtype')),
            ],
        ),
        migrations.CreateModel(
            name='SSR',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('ssr_name', models.CharField(max_length=255)),
                ('ssr_des', models.CharField(max_length=255)),
                ('ssr_point', models.IntegerField()),
                ('probability', models.FloatField(default=0.1)),
            ],
        ),
        migrations.CreateModel(
            name='SeatDistribution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seat_count', models.IntegerField(default=0)),
                ('aircraft_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='flight.aircraft')),
                ('class_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='flight.classtype')),
            ],
        ),
        migrations.CreateModel(
            name='PnrPassenger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_dtz', models.DateTimeField(auto_now=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('nationality', models.CharField(blank=True, max_length=255, null=True)),
                ('contact_no', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('contact_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('doc_id', models.CharField(blank=True, max_length=10, null=True)),
                ('doc_type', models.CharField(blank=True, max_length=10, null=True)),
                ('scd1', models.CharField(blank=True, max_length=255, null=True)),
                ('scd2', models.CharField(blank=True, max_length=255, null=True)),
                ('ssr', models.IntegerField(default=0)),
                ('recloc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flight.pnr')),
            ],
        ),
        migrations.CreateModel(
            name='PnrFlightMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flight.flight')),
                ('pnr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flight.pnr')),
            ],
        ),
        migrations.CreateModel(
            name='FlightScheduleDate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flight.flightschedule')),
            ],
        ),
        migrations.AddField(
            model_name='flight',
            name='schedule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='flight.flightschedule'),
        ),
    ]
