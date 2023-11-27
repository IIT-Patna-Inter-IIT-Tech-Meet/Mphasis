from flight.models import Flight, PNR, PnrFlightMapping, Airport, SeatDistribution
from app.config import settings
from datetime import timedelta
from django.db.models import Count, F, Sum

def cancelled_flight():
    cancelled_flights = Flight.objects.filter(status="red")
    data = []
    for flight in cancelled_flights:
        data.append(
            {
                "flight_id": flight.id,
                "flight_number": flight.flight_number,
                "departure_airport": flight.departure_airport_id.iata_code,
                "arrival_airport": flight.arrival_airport_id.iata_code,
                "status": flight.status,
                "aircraft": flight.aircraft_id.registration,
                "owner": flight.aircraft_id.owner_name,
                "arrival_time": flight.arrival_time,
                "departure_time": flight.departure_time,
            }
        )
    return data


def util_pnr_ranking(flight_id):
    try:
        flight = Flight.objects.get(id=flight_id)
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
        flight = Flight.objects.get(id=flight_id)
    except Flight.DoesNotExist:
        return {"error": "Flight does not exist"}

    # get all neighbouring source and dst airport
    # lets take other airport from same state
    src = flight.departure_airport_id
    dst = flight.arrival_airport_id

    time_threshold = flight.arrival_time + timedelta(hours=48)

    n_src = Airport.objects.filter(iso_region=src.iso_region).exclude(iata_code="")
    n_dst = Airport.objects.filter(iso_region=dst.iso_region).exclude(iata_code="")

    # get all flights from sources to dsts
    alt_flights = Flight.objects.filter(
        departure_airport_id__in=n_src, arrival_airport_id__in=n_dst, status="green", arrival_time__lte=time_threshold
    ).order_by("-flight_time")
    data = []
    for flight in alt_flights:
        # get no of free-seat for each flight
        total_seats = SeatDistribution.objects.filter(
            aircraft_id = flight.aircraft_id,
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


        data.append(
            {
                "flight_id": flight.id,
                "flight_number": flight.flight_number,
                "departure_airport": flight.departure_airport_id.iata_code,
                "arrival_airport": flight.arrival_airport_id.iata_code,
                "status": flight.status,
                "arrival_time": flight.arrival_time,
                "departure_time": flight.departure_time,
                "all_seats": all_seats,
                "booked_seats": booked_seats,
            }
        )
    return data
