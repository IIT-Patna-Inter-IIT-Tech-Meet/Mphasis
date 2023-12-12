from django.http import JsonResponse
from django.shortcuts import render
from .utils import *
# Create your views here.
def all_canclled_flight(request):
    data = cancelled_flight()
    return JsonResponse(data)

def pnr_ranking(request):
    flight_id = request.GET.get("flight_id")
    data = util_pnr_ranking(flight_id)
    return JsonResponse({"data" : data})

def flight_ranking(request):
    flight_id = request.GET.get("flight_id")
    data = util_flight_ranking(flight_id)
    return JsonResponse({"data" : data})

def alt_flight_scores(request):
    original_flight_id = request.GET.get("flight_id")
    pnr_id = request.GET.get("pnr_id")
    pnr = PNR.objects.get(pnr=pnr_id)
    alt_flights = util_flight_ranking(original_flight_id)["data"]
    data = []
    for flight in alt_flights:
        flight_obj = Flight.objects.get(flight_id=flight["flight_id"])
        scoring = PNRFlightScoring(pnr, flight_obj)
        data.append(
            {
                "pnr_id": pnr_id,
                "flight_id": flight_obj.flight_id,
                "arrival_delay_cost": scoring.arrival_delay_cost,
                "departure_delay_cost": scoring.departure_delay_cost,
                "stopover_cost": scoring.stopover_cost,
                "downgrade_cost": scoring.downgrade_cost,
                "upgrade_cost": scoring.upgrade_cost,
                "same_destination_cost": scoring.same_destination_cost,
                "alt_flight_score": scoring.alt_flight_score,
                
            }
        )
        
    return JsonResponse({"data" : data})
