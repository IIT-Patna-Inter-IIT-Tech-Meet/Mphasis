
from django.urls import path, include
from flight.views import *

urlpatterns = [
    path('canclled', all_canclled_flight),
    path('pnr_ranking', pnr_ranking),
    path('alt_flight', flight_ranking),
    path('alt_flight_scores', alt_flight_scores),
    path('pnr_scores', pnr_scores),
]
