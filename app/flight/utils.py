from flight.models import (
    Flight,
    PNR,
    PnrFlightMapping,
    Airport,
    SeatDistribution,
    FlightSchedule,
    FlightScheduleDate,
    ClassType,
)
from django.utils import timezone
from app.config import settings
from datetime import timedelta
from django.db.models import Count, F, Q, Sum
import datetime


def fetch_class_cabin_mapping():
    class_cabin_mapping = {}
    classes = ClassType.objects.all()
    for c in classes:
        if c.cabin.type_name not in class_cabin_mapping:
            class_cabin_mapping[c.cabin.type_name] = []
        class_cabin_mapping[c.cabin.type_name].append(c.type_name)
    return class_cabin_mapping


CLASS_CABIN_MAPPING = fetch_class_cabin_mapping()


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
    return {"count": len(data), "data": data}


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


def get_avilable_seats(aircraft, flight, use_inventory=False, use_cabin_only=True):
    total_seats = SeatDistribution.objects.filter(
        aircraft_id=aircraft,
    )
    all_seats = {s.class_type.type_name: s.seat_count for s in total_seats}
    booked_seats = (
        PnrFlightMapping.objects.filter(flight=flight)
        .annotate(seat_type=F("pnr__seat_class__type_name"))
        .values("seat_type")
        .annotate(count=Sum("pnr__pax"))
    )
    booked_seats = {s["seat_type"]: s["count"] for s in booked_seats}
    avilaible_seats = {k: all_seats[k] - booked_seats.get(k, 0) for k in all_seats}
    
    try:
        inv = flight.avilable_inventory
    except:
        flight = Flight.objects.get(flight_id=flight)
        inv = flight.avilable_inventory

    if use_inventory:
        inventory = list(map(int, inv.split(",")))
        keys = ["F", "B", "P", "E"]
        avilaible_seats = {keys[i]: inventory[i] for i in range(len(keys))}
        use_cabin_only = False

    if use_cabin_only:
        avilable = {}
        for key, value in CLASS_CABIN_MAPPING.items():
            avilable[key] = max(sum([avilaible_seats.get(k, 0) for k in value]), 0)
        avilaible_seats = avilable

    return avilaible_seats, sum(avilaible_seats.values())


def get_one_hop_flights(
    main_flight, time_threshold, use_inventory=False, use_cabin_only=True
):
    query = f"""
        select 
            *,
            f2.flight_id as f2_id, f2.status as f2_status, f2.src_id as f2_src, f2.dst_id as f2_dst, f2.schedule_id as f2_schedule, f2.arrival as f2_arrival, f2.departure as f2_departure 
        from flight_flight as f1 inner join flight_flight as f2 
        on f1.dst_id == f2.src_id 
        where f1.src_id = {main_flight.src.id} AND
            f2.dst_id = {main_flight.dst.id}  AND
            f1.departure >= '{main_flight.departure}' AND f2.arrival <= '{time_threshold}' AND
            f1.arrival < f2.departure
            AND f1.status = 'Scheduled' AND f2.status = 'Scheduled'
    """
    # print(query)

    try:
        conn_flights = Flight.objects.raw(query)
    except Exception as e:
        print(e)
        conn_flights = []
    c_data = []
    for flight in conn_flights:
        # dict_keys(['_state', 'flight_id', 'schedule_id', 'status', 'departure', 'arrival', 'src_id', 'dst_id', 'f2_id', 'f2_status', 'f2_src', 'f2_dst', 'f2_schedule', 'f2_arrival', 'f2_departure'])
        tmp_data = []

        # 1st flight
        avilaible_seats, total_avilable_seats = get_avilable_seats(
            flight.schedule.schedule.aircraft_id, flight, use_inventory, use_cabin_only
        )

        tmp_data.append(
            {
                "flight_id": flight.flight_id,
                "departure_airport": flight.src.iata_code,
                "arrival_airport": flight.dst.iata_code,
                "status": flight.status,
                "arrival_time": flight.arrival,
                "departure_time": flight.departure,
                "total_avilable_seats": total_avilable_seats,
                "delay": flight.departure - main_flight.departure,
                "flight_time": flight.arrival - flight.departure,
                "avilable_seats": avilaible_seats,
            }
        )

        # 2nd flight
        schedule = FlightScheduleDate.objects.get(id=flight.f2_schedule).schedule
        avilaible_seats, total_avilable_seats = get_avilable_seats(
            schedule.aircraft_id, flight.f2_id, use_inventory, use_cabin_only
        )

        f2_departure = timezone.make_aware(
            flight.f2_departure, timezone.get_current_timezone()
        )

        f2_arrival = timezone.make_aware(
            flight.f2_arrival, timezone.get_current_timezone()
        )
        delay = f2_departure - flight.arrival

        tmp_data.append(
            {
                "flight_id": flight.f2_id,
                "departure_airport": Airport.objects.get(id=flight.f2_src).iata_code,
                "arrival_airport": Airport.objects.get(id=flight.f2_dst).iata_code,
                "status": flight.f2_status,
                "arrival_time": f2_arrival,
                "departure_time": f2_departure,
                "total_avilable_seats": total_avilable_seats,
                "delay": delay,
                "flight_time": f2_arrival - f2_departure,
                "avilable_seats": avilaible_seats,
            }
        )
        # if delay > timedelta(minutes=0): #: TODO : fetch from config
        c_data.append(tmp_data)

    return c_data


def get_two_hop_flights(
    main_flight, time_threshold, use_inventory=False, use_cabin_only=True
):
    query = f"""
        select 
            *,
            f2.flight_id as f2_id, f2.status as f2_status, f2.src_id as f2_src, f2.dst_id as f2_dst, f2.schedule_id as f2_schedule, 
         	f2.arrival as f2_arrival, f2.departure as f2_departure ,
            f3.flight_id as f3_id, f2.status as f3_status, f3.src_id as f3_src, f3.dst_id as f3_dst, f3.schedule_id as f3_schedule,
            f3.arrival as f3_arrival, f3.departure as f3_departure
        from flight_flight as f1 inner join flight_flight as f2 inner join flight_flight as f3
        on f1.dst_id == f2.src_id and f2.dst_id = f3.src_id
        where 
            f1.src_id = {main_flight.src.id} AND
            f1.dst_id != {main_flight.dst.id} AND
            f3.dst_id = {main_flight.dst.id}  AND
            f3.src_id != {main_flight.src.id}  AND
            f1.departure >= '{main_flight.departure}'
            AND f3.arrival <= '{time_threshold}' 
            AND f1.arrival < f2.departure
            AND f2.arrival < f3.departure
            AND f1.status = 'Scheduled' AND f2.status = 'Scheduled' AND f3.status = 'Scheduled';
    """
    # print(query)

    try:
        conn_flights = Flight.objects.raw(query)
    except Exception as e:
        print("Error", e)
        conn_flights = []

    c_data = []

    for flight in conn_flights:
        # dict_keys(['_state', 'flight_id', 'schedule_id', 'status', 'departure', 'arrival', 'src_id', 'dst_id', 'f2_id', 'f2_status', 'f2_src', 'f2_dst', 'f2_schedule', 'f2_arrival', 'f2_departure'])
        tmp_data = []

        # 1st flight
        avilaible_seats, total_avilable_seats = get_avilable_seats(
            flight.schedule.schedule.aircraft_id, flight, use_inventory, use_cabin_only
        )
        tmp_data.append(
            {
                "flight_id": flight.flight_id,
                "departure_airport": flight.src.iata_code,
                "arrival_airport": flight.dst.iata_code,
                "status": flight.status,
                "arrival_time": flight.arrival,
                "departure_time": flight.departure,
                "total_avilable_seats": total_avilable_seats,
                "delay": flight.departure - main_flight.departure,
                "flight_time": flight.arrival - flight.departure,
                "avilable_seats": avilaible_seats,
            }
        )

        # 2nd flight
        schedule = FlightScheduleDate.objects.get(id=flight.f2_schedule).schedule
        avilaible_seats, total_avilable_seats = get_avilable_seats(
            schedule.aircraft_id, flight.f2_id, use_inventory, use_cabin_only
        )

        f2_departure = timezone.make_aware(
            flight.f2_departure, timezone.get_current_timezone()
        )

        f2_arrival = timezone.make_aware(
            flight.f2_arrival, timezone.get_current_timezone()
        )
        delay = f2_departure - flight.arrival

        tmp_data.append(
            {
                "flight_id": flight.f2_id,
                "departure_airport": Airport.objects.get(id=flight.f2_src).iata_code,
                "arrival_airport": Airport.objects.get(id=flight.f2_dst).iata_code,
                "status": flight.f2_status,
                "arrival_time": f2_arrival,
                "departure_time": f2_departure,
                "total_avilable_seats": total_avilable_seats,
                "delay": delay,
                "flight_time": f2_arrival - f2_departure,
                "avilable_seats": avilaible_seats,
            }
        )

        # 3rd flight
        schedule = FlightScheduleDate.objects.get(id=flight.f3_schedule).schedule
        avilaible_seats, total_avilable_seats = get_avilable_seats(
            schedule.aircraft_id, flight.f3_id, use_inventory, use_cabin_only
        )

        f3_departure = timezone.make_aware(
            flight.f3_departure, timezone.get_current_timezone()
        )

        f3_arrival = timezone.make_aware(
            flight.f3_arrival, timezone.get_current_timezone()
        )
        delay = f3_departure - f2_arrival

        tmp_data.append(
            {
                "flight_id": flight.f3_id,
                "departure_airport": Airport.objects.get(id=flight.f3_src).iata_code,
                "arrival_airport": Airport.objects.get(id=flight.f3_dst).iata_code,
                "status": flight.f3_status,
                "arrival_time": f3_arrival,
                "departure_time": f3_departure,
                "total_avilable_seats": total_avilable_seats,
                "delay": delay,
                "flight_time": f3_arrival - f3_departure,
                "avilable_seats": avilaible_seats,
            }
        )

        # if delay > timedelta(minutes=0): #: TODO : fetch from config
        c_data.append(tmp_data)

    return c_data


def util_flight_ranking(flight_id, max_hop=2, use_inventory=False, use_cabin_only=True, neighboring_search=True):
    # get source airport, and dst airport
    try:
        main_flight = Flight.objects.get(flight_id=flight_id)
    except Flight.DoesNotExist:
        return {"error": "Flight does not exist"}

    # get all neighbouring source and dst airport
    # lets take other airport from same state
    src = main_flight.src
    dst = main_flight.dst

    time_threshold = main_flight.arrival + timedelta(hours=72)

    if neighboring_search:
        n_src = Airport.objects.filter(iso_region=src.iso_region).exclude(iata_code="")
        n_dst = Airport.objects.filter(iso_region=dst.iso_region).exclude(iata_code="")
    else:
        n_src = [src]
        n_dst = [dst]

    # get all flights from sources to dsts
    alt_flights = Flight.objects.filter(
        dst__in=n_src,
        src__in=n_dst,
        status="Scheduled",
        arrival__lte=time_threshold,
        departure__gte=main_flight.departure,
    ).order_by("arrival")

    data = []
    for flight in alt_flights:
        avilaible_seats, total_avilable_seats = get_avilable_seats(
            flight.schedule.schedule.aircraft_id, flight, use_inventory, use_cabin_only
        )

        data.append(
            {
                "flight_id": flight.flight_id,
                "departure_airport": flight.src.iata_code,
                "arrival_airport": flight.dst.iata_code,
                "status": flight.status,
                "arrival_time": flight.arrival,
                "departure_time": flight.departure,
                "total_avilable_seats": total_avilable_seats,
                "delay": flight.departure - main_flight.departure,
                "flight_time": flight.arrival - flight.departure,
                "avilable_seats": avilaible_seats,
            }
        )

    related_canclled_flights = Flight.objects.filter(
        status="Cancelled", src__in=n_src, dst__in=n_dst
    )
    r_flights = []
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

    c_data = (
        get_one_hop_flights(main_flight, time_threshold, use_inventory, use_cabin_only)
        if max_hop >= 1
        else []
    )
    t_data = (
        get_two_hop_flights(main_flight, time_threshold, use_inventory, use_cabin_only)
        if max_hop >= 2
        else []
    )

    return {
        "data": data,
        "r_flights": r_flights,
        "c_flights": c_data,
        "t_flights": t_data,
    }
