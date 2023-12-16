from django.http import JsonResponse
from app.config import settings
from .utils import *


# Create your views here.
def all_canclled_flight(request):
    data = cancelled_flight()
    return JsonResponse(data)


def pnr_ranking(request):
    flight_id = request.GET.get("flight_id")
    data = util_pnr_ranking(flight_id)
    return JsonResponse(data)


def flight_ranking(request):
    flight_id = request.GET.get("flight_id")
    max_hop = int(settings["search"]["max_hop"])
    data = util_flight_ranking(flight_id, max_hop, use_inventory=False)
    return JsonResponse(data)
