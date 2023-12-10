from flight.models import Flight, PNR, PnrFlightMapping, Airport, SeatDistribution, PnrPassenger
from app.config import settings
from datetime import timedelta, datetime
from django.db.models import Count, F, Sum

SAFE = settings["safe"]
SSR_SCORE = settings["ssr_score"]
PAX_SCORE = settings["pax_score"]
PAID_SERVICES_SCORE = settings["paid_service_score"]
LOYALTY_SCORE = settings["loyality_program_score"]
CONNECTION_SCORE = settings["connecting_score"]
MAX_ARRIVAL_SCORE = settings["max_arrival_score"]
MIN_ARRIVAL_SCORE = settings["min_arrival_score"]
MAX_DEPARTURE_SCORE = settings["max_departure_score"]
MIN_DEPARTURE_SCORE = settings["min_departure_score"]
DO_DOWNGRADE = settings["downgrade"]
DO_UPGRADE = settings["upgrade"]

def cancelled_flight():
    cancelled_flights = Flight.objects.filter(status="Cancelled")
    data = []
    for flight in cancelled_flights:
        data.append(
            {
                "flight_id": flight.flight_id,
                "departure_airport": flight.src.iata_code,
                "arrival_airport": flight.dst.iata_code,
                "status": flight.status,
                "arrival_time": flight.arrival,
                "departure_time": flight.departure,
            }
        )
    return data


def util_pnr_ranking(flight_id):
    try:
        flight = Flight.objects.get(flight_id=flight_id)
    except Flight.DoesNotExist:
        return {"error": "Flight does not exist"}

    data = []

    pnrs = PnrFlightMapping.objects.filter(flight=flight).order_by("-pnr__score")
    for pnr in pnrs:
        data.append(
            {
                "pnr": pnr.pnr.pnr,
                "score": pnr.pnr.score,
                "class": pnr.pnr.seat_class.type_name,
                "pax": pnr.pnr.pax,
            }
        )
    return data


def util_flight_ranking(flight_id):
    # get source airport, and dst airport
    try:
        flight = Flight.objects.get(flight_id=flight_id)
    except Flight.DoesNotExist:
        return {"error": "Flight does not exist"}

    # get all neighbouring source and dst airport
    # lets take other airport from same state
    src = flight.src
    dst = flight.dst

    time_threshold = flight.arrival + timedelta(hours=48)

    n_src = Airport.objects.filter(iso_region=src.iso_region).exclude(iata_code="")
    n_dst = Airport.objects.filter(iso_region=dst.iso_region).exclude(iata_code="")


    # get all flights from sources to dsts
    alt_flights = Flight.objects.filter(
        dst__in=n_src, src__in=n_dst, status="Scheduled", arrival__lte=time_threshold
    ).order_by("arrival")
    data = []
    for flight in alt_flights:
        # get no of free-seat for each flight
        total_seats = SeatDistribution.objects.filter(
            aircraft_id = flight.schedule.schedule.aircraft_id,
        )
        all_seats = {s.class_type.type_name: s.seat_count for s in total_seats}
        booked_seats = PnrFlightMapping.objects.filter(flight=flight).annotate(
            seat_type=F("pnr__seat_class__type_name")
        ).values(
            "seat_type"
        ).annotate(
            count=Sum("pnr__pax")
        )
        booked_seats = {s["seat_type"]: s["count"] for s in booked_seats}
        avilaible_seats = {k: all_seats[k] - booked_seats.get(k, 0) for k in all_seats}


        data.append(
            {
                "flight_id": flight.flight_id,
                "departure_airport": flight.src.iata_code,
                "arrival_airport": flight.dst.iata_code,
                "status": flight.status,
                "arrival_time": flight.arrival,
                "departure_time": flight.departure,
                "total_avilable_seats" : sum(all_seats.values()) - sum(booked_seats.values()),
                "avilable_seats": avilaible_seats,
                # "all_seats": all_seats,
                # "booked_seats": booked_seats,
            }
        )

    related_canclled_flights = Flight.objects.filter(status="Cancelled", src__in=n_src, dst__in=n_dst)
    r_flights= []
    for flight in related_canclled_flights:
        r_flights.append(
            {
                "flight_id": flight.flight_id,
                "departure_airport": flight.src.iata_code,
                "arrival_airport": flight.dst.iata_code,
                "status": flight.status,
                "arrival_time": flight.arrival,
                "departure_time": flight.departure,
            }
        )

    return {"data": data, "r_flights" : r_flights }

class PNRScoring:
    def __init__(self, pnr):
        self.pnr = pnr
        
        self.class_score = self.get_class_score()
        self.pax_score = self.get_pax_score()
        self.group_score = self.get_group_score()
        self.paid_services_score = self.get_paid_services_score()
        self.loyalty_score = self.get_loyalty_score()
        self.connection_score = self.get_connection_score()
        self.ssr_score = self.get_ssr_score()
        self.pnr_score = self.get_pnr_score()
        
    def get_ssr_score(self):
        passengers = PnrPassenger.objects.filter(pnr=self.pnr)
        ssr_scores = [passenger.ssr for passenger in passengers]
        return sum(ssr_scores)*SSR_SCORE
    
    def get_class_score(self):
        return self.pnr.seat_class.score
    
    def get_pax_score(self):
        return self.pnr.pax*PAX_SCORE
    
    def get_group_score(self):
        return self.pnr.booking_type.group_point
    
    def get_paid_services_score(self):
        return self.pnr.paid_service*PAID_SERVICES_SCORE
    
    def get_loyalty_score(self):
        return self.pnr.loyalty_program*LOYALTY_SCORE
    
    def get_connection_score(self):
        return PnrFlightMapping.objects.filter(pnr=self.pnr).count()*CONNECTION_SCORE
        
    def get_pnr_score(self):
        self.class_score = self.get_class_score()
        self.pax_score = self.get_pax_score()
        self.group_score = self.get_group_score()
        self.paid_services_score = self.get_paid_services_score()
        self.loyalty_score = self.get_loyalty_score()
        self.connection_score = self.get_connection_score()
        self.ssr_score = self.get_ssr_score()
        
        return self.class_score + self.pax_score + self.group_score + self.paid_services_score + self.loyalty_score + self.connection_score + self.ssr_score
        
    

class PNRFlightScoring:
    def __init__(self, pnr, alt_flight):
        self.pnr = pnr
        self.alt_flight = alt_flight
        self.original_flight = PnrFlightMapping.objects.get(pnr=pnr).flight
        
        self.arrival_delay_cost = self.get_arrival_delay_cost()
        self.departure_delay_cost = self.get_departure_delay_cost()
        self.stopover_cost = self.get_stopover_cost()
        self.downgrade_cost = self.get_downgrade_cost()
        self.upgrade_cost = self.get_upgrade_cost()
        self.same_destination_cost = self.get_same_destination_cost()
        self.alt_flight_score = self.get_alt_flight_score()
        
        
    def get_arrival_delay_cost(self):
        delay_seconds = (self.alt_flight.arrival - self.original_flight.arrival).total_seconds()
        delay_hours = delay_seconds / 3600  # convert seconds to hours

        cost = MIN_ARRIVAL_SCORE + (48-delay_hours)/(MAX_ARRIVAL_SCORE-MIN_ARRIVAL_SCORE)
        if delay_hours>48:
            cost = 0
        return cost
        
    def get_departure_delay_cost(self):
        delay_seconds = (self.alt_flight.departure - self.original_flight.departure).total_seconds()
        delay_hours = delay_seconds / 3600  # convert seconds to hours
        cost = MIN_DEPARTURE_SCORE + (48-delay_hours)/(MAX_DEPARTURE_SCORE-MIN_DEPARTURE_SCORE)
        if delay_hours>48:
            cost = 0
        return cost
    
    def get_upgrade_cost(self):
        return 0
    
    def get_downgrade_cost(self):
        return 0
    
    def get_stopover_cost(self):
        return 0
    
    def get_same_destination_cost(self):
        return 0
    
    def get_alt_flight_score(self):
        return self.arrival_delay_cost + self.departure_delay_cost - self.upgrade_cost - self.downgrade_cost - self.stopover_cost + self.same_destination_cost
