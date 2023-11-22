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



    


