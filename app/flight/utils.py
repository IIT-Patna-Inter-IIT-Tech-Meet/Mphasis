from flight.models import Flight, PNR
from app.config import settings

def cancelled_flight():
    cancelled_flights = Flight.objects.filter(status="red")
    data = []
    for flight in cancelled_flights:
        data.append({
            "flight_id": flight.id,
            "flight_number": flight.flight_number,
            "departure_airport": flight.departure_airport_id.iata_code,
            "arrival_airport": flight.arrival_airport_id.iata_code,
            "status": flight.status,
            "aircraft": flight.aircraft_id.registration,
            "owner": flight.aircraft_id.owner_name,
            "arrival_time": flight.arrival_time,
            "departure_time": flight.departure_time,
        })
    return data

def util_pnr_ranking(flight_id):
    try:
        flight = Flight.objects.get(id=flight_id)
    except Flight.DoesNotExist:
        return {"error" : "Flight does not exist"}
    
    data = []
    pnrs = PNR.objects.filter(flight=flight_id)
    for pnr in pnrs:
        data.append({
            "pnr": pnr.id,
        })
    return data


def util_flight_ranking(flight_id):
    # get source airport, and dst airport
    try:
        flight = Flight.objects.get(id=flight_id)
    except Flight.DoesNotExist:
        return {"error" : "Flight does not exist"}
    
    
    # get all neighbouring source and dst airport
    # get all flights from sources to dsts
    print(settings.get('neighbouring_dst'))
    pass