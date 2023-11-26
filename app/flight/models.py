from django.db import models, transaction
from enum import Enum
from phonenumber_field.modelfields import PhoneNumberField
from django.db import transaction

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
    id = models.AutoField(primary_key=True, auto_created=True, unique=True)
    model = models.CharField(max_length=25, null=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    registration = models.CharField(max_length=255, null=False)
    owner_code = models.CharField(max_length=255, null=False)
    owner_name = models.CharField(max_length=255, null=False)

    def __str__(self):
        return f"[{self.registration}-{self.owner_code}]"

class ClassType(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    type_name = models.CharField(max_length=255, null=False)
    des = models.CharField(max_length=225, null=False)
    score = models.IntegerField(null=False, default=0)
    cabin = models.ForeignKey('CabinType', on_delete=models.CASCADE, null=True)
    upper = models.IntegerField(null=False, default=0)
    lower = models.IntegerField(null=False, default=0)
    
    def __str__(self):
        return f"[{self.type_name}]"

class CabinType(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    type_name = models.CharField(max_length=255, null=False)
    des = models.CharField(max_length=225, null=False)
    score = models.IntegerField(null=False, default=0)
    
    def __str__(self):
        return f"[{self.type_name}]"
    
class SSR(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    ssr_name = models.CharField(max_length=255, null=False)
    ssr_des = models.CharField(max_length=255, null=False)
    ssr_point = models.IntegerField(null=False)
    probability = models.FloatField(null=False, default=0.1)

    def __str__(self):
        return f"[{self.ssr_name}]"
    
class Group(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    group_name = models.CharField(max_length=255, null=False)
    group_des = models.CharField(max_length=255, null=False)
    group_point = models.IntegerField(null=False)
    probability = models.FloatField(null=False, default=0.2)
    
    def __str__(self):
        return f"[{self.group_name}]"
    

class SeatDistribution(models.Model):
    aircraft_id = models.ForeignKey(Aircraft, on_delete=models.DO_NOTHING, null=False)
    class_type = models.ForeignKey(ClassType, on_delete=models.DO_NOTHING, null=False)
    seat_count = models.IntegerField(null=False, default=0)
    # seat_avail = models.IntegerField(null=False, default=0) # cant map here
        
    def __str__(self):
        return f"[{self.aircraft_id}-{self.seat_count}]"
    

class Flight(models.Model):
    status_types = [
        ('green', 'landed and open for entry'),
        ('red', 'landed and no entry'),
        ('grey', 'scheduled')
    ]
    id = models. CharField(max_length=255, primary_key=True, unique=True, null=False)
    flight_number = models.CharField(max_length=255, null=False)
    aircraft_id = models.ForeignKey(Aircraft, on_delete=models.DO_NOTHING, null=False)
    departure_airport_id = models.ForeignKey(Airport, on_delete=models.DO_NOTHING, null=False, related_name='departure_airport')
    arrival_airport_id = models.ForeignKey(Airport, on_delete=models.DO_NOTHING, null=False, related_name='arrival_airport')
    departure_time = models.DateTimeField(null=False)
    arrival_time = models.DateTimeField(null=False)
    flight_time = models.IntegerField(null=False)
    status = models.CharField(max_length=255, null=False, choices=status_types)

    def __str__(self):
        return f"[{self.flight_number}-{self.aircraft_id}-{self.departure_airport_id}-{self.arrival_airport_id}]"
    
class Passenger(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=255, null=False, default="")
    phone_no = PhoneNumberField(blank=False, null=False) 
    email = models.EmailField(max_length=254, blank=False, null=False)
    
    def __str__(self):
        return f"[{self.email}]"

class PNR(models.Model):
    pnr = models.CharField(max_length=6, null=False, unique=True, primary_key=True)
    passenger = models.ForeignKey(Passenger, on_delete=models.DO_NOTHING, null=False)
    timestamp = models.DateTimeField(null=False)
    total_amount = models.FloatField(null=False, default=0)
    total_tax = models.FloatField(null=False, default=0)
    currency = models.CharField(max_length=255, null=False)
    seat_class = models.ForeignKey(ClassType, on_delete=models.DO_NOTHING, null=False)
    paid_service = models.BooleanField(null=False, default=False)
    loyalty_program = models.BooleanField(null=False, default=False)
    conn = models.IntegerField(null=False, default=0)
    pax = models.IntegerField(null=False, default=0)
    booking_type = models.ForeignKey(Group, on_delete=models.DO_NOTHING, null=False)
    ssr = models.IntegerField(null=False, default=0)

    def __str__(self):
        return f"[{self.pnr}]"
    
class PnrFlightMapping(models.Model):
    pnr = models.ForeignKey(PNR, on_delete=models.CASCADE, null=False)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, null=False)
    
    def __str__(self):
        return f"[{self.pnr}-{self.flight}]"

    
# class PassengerSeat(models.Model):
    
#     id = models.AutoField(primary_key=True, auto_created=True)
#     passenger = models.ForeignKey(Passenger, on_delete=models.DO_NOTHING, null=False)
#     pnr = models.ForeignKey('PNR', on_delete=models.CASCADE, null=False)
    
#     def save(self, *args, **kwargs):
#         try:
#             seat_distribution = SeatDistribution.objects.get(aircraft_id=self.pnr.flight.aircraft_id, class_type=self.seat_class, cabin_type=self.seat_cabin)
#             # Decrease seat_avail by one when a new PassengerSeat is created
#             with transaction.atomic():
#                 if seat_distribution.seat_avail <= 0:
#                     raise Exception("No seats available")
#                 else: 
#                     seat_distribution.seat_avail -= 1
#                     seat_distribution.save()
#         except SeatDistribution.DoesNotExist:
#             # If the SeatDistribution does not exist, create a new one
#             with transaction.atomic():
#                 seat_distribution = SeatDistribution(aircraft_id=self.pnr.flight.aircraft_id, class_type=self.pnr.seat_class, cabin_type=self.pnr.seat_cabin, seat_count=100, seat_avail=100)
#                 seat_distribution.save()
#                 if seat_distribution.seat_avail <= 0:
#                     raise Exception("No seats available")
#                 else: 
#                     seat_distribution.seat_avail -= 1
#                     seat_distribution.save()
        
#         # Calculate seat_total
#         self.seat_total = self.seat_price + self.seat_tax

#         # Call the original save method
#         super(PassengerSeat, self).save(*args, **kwargs)

#     def delete(self, *args, **kwargs):
#         try:
#             seat_distribution = SeatDistribution.objects.get(aircraft_id=self.pnr.flight.aircraft_id, class_type=self.seat_class, cabin_type=self.seat_cabin)
#             # Increase seat_avail by one when a PassengerSeat is deleted
#             with transaction.atomic():
#                 seat_distribution.seat_avail += 1
#                 seat_distribution.save()
#         except SeatDistribution.DoesNotExist:
#             # If the SeatDistribution does not exist, create a new one
#             with transaction.atomic():
#                 seat_distribution = SeatDistribution(aircraft_id=self.pnr.flight.aircraft_id, class_type=self.seat_class, cabin_type=self.seat_cabin, seat_count=100, seat_avail=100)
#                 seat_distribution.save()

#         # Call the original delete method
#         super(PassengerSeat, self).delete(*args, **kwargs)

#     def __str__(self):
#         return f"[{self.flight}-{self.passenger}-{self.seat_number}-{self.seat_class}-{self.seat_cabin}-{self.ssr}]"



