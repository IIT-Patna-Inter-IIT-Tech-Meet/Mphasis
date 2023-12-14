from django.db import models, transaction
from enum import Enum
from phonenumber_field.modelfields import PhoneNumberField
from django.db import transaction

# Create your models here.
class Airport(models.Model):
    """
    Model for Airport.
    Data : From CSV file [collected]
    Important fields:
        iata_code, continent, iso_country, iso_region, id
    Dependency:
        Null
    Populated by:
        `python3 manage.py populate_airport --clean`
    """

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
    ident = models.CharField(max_length=20, null=False)
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
        return f"[{self.iata_code}|{self.id}]"

class Aircraft(models.Model):
    """
    Model: Aircraft
    Description: Entry per aircraft
    Data: Random Entry / Dynamic Entry during FlightSchedule creation
    Important fields:
        id, total_capacity, cabin/class wise capacity
    Uncleared fields:
        *invenotry
    Dependency:
        Null
    Populated by:
        `python3 manage.py populate_aircraft --clean`
    """

    id = models.AutoField(primary_key=True, auto_created=True, unique=True)
    model = models.CharField(max_length=25, null=False) # aircraft type 
    name = models.CharField(max_length=255, null=True, blank=True)
    registration = models.CharField(max_length=255, null=False)
    owner_code = models.CharField(max_length=255, null=False)
    owner_name = models.CharField(max_length=255, null=False)
    total_capacity = models.IntegerField(null=False, default=0)
    total_invenotry = models.IntegerField(null=False, default=0)

    def __str__(self):
        return f"[{self.registration}-{self.owner_code}]"

class ClassType(models.Model):
    """
    Model : ClassType
    Description: Entry per class type
    Data: Crafted Data / Dynamic Entry during FlightSchedule creation
    Important fields:
        id, mapped cabin type, mapped seat distribution
    Dependency:
        CabinType
    Populated by:
        `python3 manage.py populate_basic --clean`
    """

    id = models.AutoField(primary_key=True, auto_created=True)
    type_name = models.CharField(max_length=255, null=False)
    des = models.CharField(max_length=225, null=False)
    score = models.IntegerField(null=False, default=0)
    cabin = models.ForeignKey('CabinType', on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return f"[{self.type_name}]"

class CabinType(models.Model):
    """
    Model: CabinType
    Description: Entry per cabin type
    Data: Crafted Data / Dynamic Entry during FlightSchedule creation
    Important fields:
        id, total_capacity, type name 
    Assumption:
        Buisness, Economy, First, Premium Economy > these are considered as cabin type
    Dependency:
        Null
    Populated by:
        `python3 manage.py populate_basic --clean`
    """
    id = models.AutoField(primary_key=True, auto_created=True)
    type_name = models.CharField(max_length=255, null=False)
    des = models.CharField(max_length=225, null=False)
    score = models.IntegerField(null=False, default=0)
    
    def __str__(self):
        return f"[{self.type_name}]"
    
class SSR(models.Model):
    """
    Model: SSR
    Description: Special Service Request
    Data: Crafted Data / Dynamic Entry during FlightSchedule creation
    Important fields:
        id, ssr_point
    Dependency:
        Null
    Populated by:
        `python3 manage.py populate_basic --clean`
    """
    id = models.AutoField(primary_key=True, auto_created=True)
    ssr_name = models.CharField(max_length=255, null=False)
    ssr_des = models.CharField(max_length=255, null=False)
    ssr_point = models.IntegerField(null=False)
    probability = models.FloatField(null=False, default=0.1)

    def __str__(self):
        return f"[{self.ssr_name}]"
    
class Group(models.Model):
    """
    Model: Group
    Description: Entry per group
    Data: Crafted Data / Dynamic Entry during FlightSchedule creation
    Important fields:
        id, group_point
    Dependency:
        Null
    Populated by:
        `python3 manage.py populate_basic --clean`
    """
    id = models.AutoField(primary_key=True, auto_created=True)
    group_name = models.CharField(max_length=255, null=False)
    group_des = models.CharField(max_length=255, null=False)
    group_point = models.IntegerField(null=False)
    probability = models.FloatField(null=False, default=0.2)
    
    def __str__(self):
        return f"[{self.group_name}]"

class Carrier(models.Model):
    """
    Model: Carrier
    Description: Entry per carrier, don't know what it is
    Data: Random Entry
    Important fields:
        code, desc
    Dependency:
        Null
    Populated by:
        `python3 manage.py populate_basic --clean`
    """
    code = models.CharField(max_length=5, null=False, primary_key=True)
    desc = models.CharField(max_length=255, null=False)

class SeatDistribution(models.Model):
    """
    Model: SeatDistribution
    Description: Multiple entry for a single aircraft
    Data: Dynamic Entry during FlightSchedule creation
    Important fields:
        aircraft_id, class_type, seat_count
    Dependency:
        Aircraft, ClassType, CabinType
    Data: Distributed
    Populated by:
        `python3 manage.py populate_aircraft --clean`
    """
    aircraft_id = models.ForeignKey(Aircraft, on_delete=models.DO_NOTHING, null=False)
    class_type = models.ForeignKey(ClassType, on_delete=models.DO_NOTHING, null=False)
    seat_count = models.IntegerField(null=False, default=0)
    # seat_avail = models.IntegerField(null=False, default=0) # cant map here
        
    def __str__(self):
        return f"[{self.aircraft_id}-{self.seat_count}]"
    

class FlightSchedule(models.Model):
    """
    Model: Flight Schedule
    Description: 
        Some aircraft have fixed schedule, they run on specfics time on every week
        from same source to same destination.
        
        For safegraud, there is FlightScheduleDate model, which ensures which date it runs.
    Assumption:
        The status field is used for determining the status of 1st upcoming flight.
    Dependency:
        Aircraft, Airport, Carrier
    Populated by:
        `python3 manage.py populate_flight --clean`
    """

    status_types = [
        ('Scheduled', 'Booking open'),
        ('Planning', 'Booking not allowed'),
        ('Canclled', 'Time to reschedule')
    ]
    id = models.CharField(max_length=255, primary_key=True, unique=True, null=False) # Schedule ID
    carrier_cd = models.ForeignKey(Carrier, on_delete=models.DO_NOTHING, null=True)
    # flight_number = models.CharField(max_length=255, null=False)
    aircraft_id = models.ForeignKey(Aircraft, on_delete=models.DO_NOTHING, null=False)
    departure_airport = models.ForeignKey(Airport, on_delete=models.DO_NOTHING, null=False, related_name='departure_airport')
    arrival_airport = models.ForeignKey(Airport, on_delete=models.DO_NOTHING, null=False, related_name='arrival_airport')
    departure_time = models.TimeField(null= True)
    arrival_time = models.TimeField(null=False)
    start_date = models.DateField(null = True)
    end_date = models.DateField(null= True)
    # weekly shcedule 
    r_sun = models.BooleanField(default= False)
    r_mon = models.BooleanField(default= False)
    r_tue = models.BooleanField(default= False)
    r_wed = models.BooleanField(default= False)
    r_thr = models.BooleanField(default= False)
    r_fri = models.BooleanField(default= False)
    r_sat = models.BooleanField(default= False)

    freq = models.IntegerField(default= 0)
    dept_count = models.IntegerField(default=0)
    status = models.CharField(max_length=255, null=False, choices=status_types)

    def __str__(self):
        return f"[{self.id}-{self.aircraft_id}]"

class FlightScheduleDate(models.Model):
    """
    Model: FlightScheduleDate
    Description:
        This models ensures which date the flight will run.
        A one to many relationship with FlightSchedule
    Populated by:
        `python3 manage.py populate_flight --clean`
    """
    schedule = models.ForeignKey(FlightSchedule, on_delete=models.CASCADE, null=False)
    date = models.DateField(null=False)

    def __str__(self):
        return f"[{self.schedule}-{self.date}]"


class Flight(models.Model):
    """
    Model: Flight
    Description: 
        This model acts as a bridge between FlightSchedule and PNR
        ideally, this should be cancelled during the flight schedule cancellation
        One to One mappring with FlightScheduleDate
    Populated by:
        `python3 manage.py populate_flight --clean`
    """
    status_types = [
        ('Scheduled', 'Booking open'),
        ('Planning', 'Booking not allowed'),
        ('Canclled', 'Time to reschedule')
    ]

    flight_id = models.CharField(max_length=255, null=False, primary_key=True, unique=True)
    schedule = models.ForeignKey(FlightScheduleDate, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=255, null=False, choices=status_types)
    departure = models.DateTimeField(null=True)
    arrival = models.DateTimeField(null=True)
    src = models.ForeignKey(Airport, on_delete=models.DO_NOTHING, null=True, related_name='src')
    dst = models.ForeignKey(Airport, on_delete=models.DO_NOTHING, null=True, related_name='dst')
    dep_key = models.CharField(max_length=255, null=True, blank=True, default = "") # DEP_KEY : DON'T know what it is
    avilable_inventory = models.CharField(max_length=255, null=True, blank=True, default="")

class PNR(models.Model):
    """
    Model: PNR
    Description:
        PNR generated for each booking, multiple passenger can be booked under same PNR
        Also multiple flight can be connected under same PNR

    Scoring Fields:
        seat_class, seat_class->seat_cabin
        paid_service
        loyalty_program
        conn
        pax
        booking_type
            sum(PnrPassenger->ssr)
        
    Populated by:
        `python3 manage.py populate_pnr --clean`
    """
    pnr = models.CharField(max_length=6, null=False, unique=True, primary_key=True)
    timestamp = models.DateTimeField(null=False, auto_now=True)
    dep_key = models.CharField(max_length=255, null=True, blank=True) # DEP_KEY : DON'T know what it is
    status = models.CharField(max_length=10, null=True) # ACTION_CD
    seat_class = models.ForeignKey(ClassType, on_delete=models.DO_NOTHING, null=False) # COS_CD
    seg_seq = models.IntegerField(null=False, default=0) # SEG_SEQ : DON"T know what it is
    carrier_cd = models.CharField(max_length=5, null= True, blank= True) # CARRIER_CD ambigious field
    paid_service = models.BooleanField(null=False, default=False) # if the pnr booking have opted for paid_servcice
    loyalty_program = models.BooleanField(null=False, default=False) # if user have opted for loaylti program 
    conn = models.IntegerField(null=False, default=0) # if connecting flight
    pax = models.IntegerField(null=False, default=0) # PAX_CNT
    booking_type = models.ForeignKey(Group, on_delete=models.DO_NOTHING, null=True) # Normal, Student, Army etc.
    score = models.IntegerField(null=False, default=0)

    def __str__(self):
        return f"[{self.pnr}]"
    
class PnrFlightMapping(models.Model):
    """
    Many to Many mapping between PNR and Flight
    Dependency:
        PNR, Flight
    Populated by:
        `python3 manage.py populate_pnr --clean`
    """
    pnr = models.ForeignKey(PNR, on_delete=models.CASCADE, null=False)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, null=False)
    
    def __str__(self):
        return f"[{self.pnr}-{self.flight}]"

    
class PnrPassenger(models.Model):
    """
    Model: PnrPassenger
    Description:
        Passenger details for each PNR
        One to many mapping with PNR
    Scoring Fields:
        ssr
    Irrelevant Fields:
        scd1, scd2 ( this should not be here )
    Populated by:
        `python3 manage.py populate_pnr --clean`
    Dependency:
        PNR
    """
    recloc = models.ForeignKey(PNR, on_delete=models.CASCADE, null=False)
    creation_dtz = models.DateTimeField(null=False, auto_now=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    nationality = models.CharField(max_length=255, null=True, blank=True, default='IN')
    contact_no = PhoneNumberField(blank=True, null=True)
    contact_email = models.EmailField(max_length=254, blank=True, null=True)
    doc_id = models.CharField(max_length=10, null=True, blank=True)
    doc_type = models.CharField(max_length=10, null=True, blank=True)
    scd1 = models.CharField(max_length=255, null=True, blank=True)
    scd2 = models.CharField(max_length=255, null=True, blank=True)
    ssr = models.IntegerField(null=False, default=0)

    def __str__(self):
        return f"[{self.recloc}-{self.last_name}-{self.first_name}]"





