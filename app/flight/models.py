from django.db import models
from enum import Enum
from django.contrib.postgres.fields import ArrayField
from phonenumber_field.modelfields import PhoneNumberField

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
    types = [
        ('A', 'First Class'),
        ('C', 'Business Class'),
        ('K', 'Economy Class')
    ]
    
    id = models.AutoField(primary_key=True, auto_created=True)
    type_name = models.CharField(max_length=255, null=False, choices=types)

class CabinType(models.Model):
    types = [
        ('F', 'First Cabin'),
        ('J', 'Second Cabin'),
        ('Y', 'Third Cabin')
    ]
    
    id = models.AutoField(primary_key=True, auto_created=True)
    type_name = models.CharField(max_length=255, null=False, choices=types)

class SeatDistribution(models.Model):
    aircraft_id = models.ForeignKey(Aircraft, on_delete=models.CASCADE, null=False)
    class_type = models.ForeignKey(ClassType, on_delete=models.CASCADE, null=False)
    cabin_type = models.ForeignKey(CabinType, on_delete=models.CASCADE, null=False)
    seat_count = models.IntegerField(null=False, default=0)
    seat_avail = models.IntegerField(null=False, default=0)


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
    
class Passenger(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    first_name = models.CharField(max_length=255, null=False)
    last_name = models.CharField(max_length=255, null=False)
    phone_no = PhoneNumberField(blank=False, null=False) 
    email = models.EmailField(max_length=254, blank=False, null=False)
    
    def __str__(self):
        return f"[{self.first_name}-{self.last_name}-{self.phone_no}-{self.email}]"
    
class PassengerSeat(models.Model):
    ssr_types = [
        ('INFT' , 'Infant'),
        ('WCHR' , 'Wheelchair, can walk'),
        ('WCHS' , 'Wheelchair, can\'t climb stairs'),
        ('WCHC' , 'Complete immobile'),
        ('LANG' , 'Language restrictions'),
        ('CHLD' , 'Child'),
        ('MAAS' , 'Meet and assist - many reasons'),
        ('UNMR' , 'Unaccompanied minor'),
        ('BLND' , 'Blind'),
        ('DEAF' , 'Deaf'),
        ('EXST' , 'Large person taking up two seats'),
        ('MEAL' , 'Meal request'),
        ('NSST' , 'seat information'),
        ('NRPS' , 'No seat request')
    ]
    
    id = models.AutoField(primary_key=True, auto_created=True)
    passenger = models.ForeignKey('passenger.Passenger', on_delete=models.CASCADE, null=False)
    pnr = models.ForeignKey('PNR', on_delete=models.CASCADE, null=False)
    seat_number = models.CharField(max_length=255, null=False)
    seat_class = models.ForeignKey(ClassType, on_delete=models.CASCADE, null=False)
    seat_cabin = models.ForeignKey(CabinType, on_delete=models.CASCADE, null=False)
    seat_price = models.FloatField(null=False, default=0)
    seat_tax = models.FloatField(null=False, default=0)
    seat_total = models.FloatField(null=False, default=0)
    ssr = models.CharField(max_length=255, null=True, choices=ssr_types)
    paid_service = models.BooleanField(null=False, default=False)
    loyalty_program = models.BooleanField(null=False, default=False)
    
    def save(self, *args, **kwargs):
        try:
            seat_distribution = SeatDistribution.objects.get(aircraft_id=self.pnr.flight.aircraft_id, class_type=self.seat_class, cabin_type=self.seat_cabin)
            # Decrease seat_avail by one when a new PassengerSeat is created
            with transaction.atomic():
                seat_distribution.seat_avail -= 1
                seat_distribution.save()
        except SeatDistribution.DoesNotExist:
            # If the SeatDistribution does not exist, create a new one
            seat_distribution = SeatDistribution(aircraft_id=self.pnr.flight.aircraft_id, class_type=self.seat_class, cabin_type=self.seat_cabin, seat_count=0, seat_avail=0)
            seat_distribution.save()
        
        # Calculate seat_total
        self.seat_total = self.seat_price + self.seat_tax

        # Call the original save method
        super(PassengerSeat, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            seat_distribution = SeatDistribution.objects.get(aircraft_id=self.pnr.flight.aircraft_id, class_type=self.seat_class, cabin_type=self.seat_cabin)
            # Increase seat_avail by one when a PassengerSeat is deleted
            with transaction.atomic():
                seat_distribution.seat_avail += 1
                seat_distribution.save()
        except SeatDistribution.DoesNotExist:
            # If the SeatDistribution does not exist, create a new one
            seat_distribution = SeatDistribution(aircraft_id=self.pnr.flight.aircraft_id, class_type=self.seat_class, cabin_type=self.seat_cabin, seat_count=100, seat_avail=100)
            seat_distribution.save()

        # Call the original delete method
        super(PassengerSeat, self).delete(*args, **kwargs)

    def __str__(self):
        return f"[{self.flight}-{self.passenger}-{self.seat_number}-{self.seat_class}-{self.seat_cabin}-{self.ssr}]"

class PNR(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, null=False)
    seats = models.ManyToManyField(PassengerSeat)
    timestamp = models.DateTimeField(null=False)
    total_tax = models.FloatField(null=False, default=0)
    total_price = models.FloatField(null=False, default=0)
    seat_currency = models.CharField(max_length=255, null=False)
    paid_service = models.BooleanField(null=False, default=False)
    group_booking = models.BooleanField(null=False, default=False)
    loyalty_program = models.BooleanField(null=False, default=False)

    def save(self, *args, **kwargs):
        # Sum up the total prices of all PassengerSeat instances
        self.total_tax = sum(seat.seat_tax for seat in self.seats.all())
        self.total_price = sum(seat.seat_total for seat in self.seats.all())
        self.paid_service = any(seat.paid_service for seat in self.seats.all())
        self.group_booking = len(self.seats.all()) > 1
        self.loyalty_program = any(seat.loyalty_program for seat in self.seats.all())
        super(PNR, self).save(*args, **kwargs)

    def __str__(self):
        return f"[{self.id}-{self.flight}-{self.total_price}-{self.seat_currency}]"


