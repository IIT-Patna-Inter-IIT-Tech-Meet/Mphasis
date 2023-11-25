from django.http import JsonResponse
from django.shortcuts import render
from .models import Flight, PNR
# Create your views here.
def all_canclled_flight(request):
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
    return JsonResponse({"data" : data})

def pnr_ranking(request):
    flight_id = request.GET.get("flight_id")
    try:
        flight = Flight.objects.get(id=flight_id)
    except Flight.DoesNotExist:
        return JsonResponse({"error" : "Flight does not exist"})
    
    data = []
    pnrs = PNR.objects.filter(flight=flight_id)
    for pnr in pnrs:
        data.append({
            "pnr": pnr.id,
        })
    return JsonResponse({"data" : data})
