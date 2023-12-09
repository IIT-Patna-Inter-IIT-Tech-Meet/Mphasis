from flight.models import Flight, PNR, PnrFlightMapping, Airport, SeatDistribution
from app.config import settings
from datetime import timedelta
from django.db.models import Count, F, Sum

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
