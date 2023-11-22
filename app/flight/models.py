from django.db import models
from enum import Enum

# Create your models here.
class Airport(models.Model):
    airport_types = [
        ('large_airport', 'Large Airport'),
        ('medium_airport', 'Medium Airport'),
        ('small_airport', 'Small Airport'),
        ('heliport', 'Heliport'),
        ('closed', 'Closed'),
        ('seaplane_base', 'Seaplane Base'),
        ('balloonport', 'Balloonport')
    ]

    id = models.IntegerField(primary_key=True, unique=True, null=False)
    ident = models.CharField(max_length=4, null=False)
    type = models.CharField(max_length=255, null=False, choices=airport_types)
    name = models.CharField(max_length=255, null=False)
    latitude_deg = models.FloatField(null=False)
    longitude_deg = models.FloatField(null=False)
    elevation_ft = models.IntegerField(null=True, blank=True)
    continent = models.CharField(max_length=2, null=True)
    continent_name = models.CharField(max_length=255, null=True)
    iso_country = models.CharField(max_length=2, null=False)
    iso_region = models.CharField(max_length=7, null=False)
    local_region = models.CharField(max_length=255, null=True)
    municipality = models.CharField(max_length=255, null=True)
    scheduled_service = models.BooleanField(null=False)
    gps_code = models.CharField(max_length=4, null=True)
    iata_code = models.CharField(max_length=3, null=True)
    local_code = models.CharField(max_length=4, null=True)
    home_link = models.URLField(null=True)
    wikipedia_link = models.URLField(null=True)
    keywords = models.CharField(max_length=255, null=True)
    score = models.IntegerField(null=True)

    def __str__(self):
        return f"[{self.iata_code}-{self.ident}]"

class Aircraft(models.Model):
    id = models.CharField(max_length=255, primary_key=True, unique=True, null=False)
    model = models.CharField(max_length=25, null=False)
    name = models.CharField(max_length=255, null=False)
    registration = models.CharField(max_length=255, null=False)
    owner_code = models.CharField(max_length=255, null=False)
    owner_name = models.CharField(max_length=255, null=False)
    cabin_type = models.CharField(max_length=255, null=False, blank=True)

    def __str__(self):
        return f"[{self.id_num}-{self.id_callsign}]"

class ClassType(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    type_name = models.CharField(max_length=255, null=False)

class CabinType(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    type_name = models.CharField(max_length=255, null=False)

class SeatDistribution(models.Model):
    aircraft_id = models.ForeignKey(Aircraft, on_delete=models.CASCADE, null=False)
    class_type = models.ForeignKey(ClassType, on_delete=models.CASCADE, null=False)
    cabin_type = models.ForeignKey(CabinType, on_delete=models.CASCADE, null=False)
    seat_count = models.IntegerField(null=False, default=0)


class Flight(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    flight_number = models.CharField(max_length=255, null=False)
    aircraft_id = models.ForeignKey(Aircraft, on_delete=models.CASCADE, null=False)
    departure_airport_id = models.ForeignKey(Airport, on_delete=models.CASCADE, null=False, related_name='departure_airport')
    arrival_airport_id = models.ForeignKey(Airport, on_delete=models.CASCADE, null=False, related_name='arrival_airport')
    departure_time = models.DateTimeField(null=False)
    arrival_time = models.DateTimeField(null=False)
    flight_time = models.IntegerField(null=False)
    status = models.CharField(max_length=255, null=False)

    def __str__(self):
        return f"[{self.flight_number}-{self.aircraft_id}-{self.departure_airport_id}-{self.arrival_airport_id}]"

    


