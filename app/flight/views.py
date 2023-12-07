from django.http import JsonResponse
from django.shortcuts import render
from .utils import *
# Create your views here.
def all_canclled_flight(request):
    data = cancelled_flight()
    return JsonResponse({"data" : data})

def pnr_ranking(request):
    flight_id = request.GET.get("flight_id")
    print(flight_id)
    data = util_pnr_ranking(flight_id)
    return JsonResponse({"data" : data})

def flight_ranking(request):
    flight_id = request.GET.get("flight_id")
    data = util_flight_ranking(flight_id)
    return JsonResponse( data )