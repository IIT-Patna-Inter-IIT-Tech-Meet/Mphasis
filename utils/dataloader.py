import requests
import json

HOST = "http://127.0.0.1:8000/"
API_CANCLED = "canclled"
API_PNR_RANKING = "pnr_ranking?flight_id="
API_ALT_FLIGHT="alt_flight?flight_id="

def get_cancled():
    response = requests.request("GET", HOST + API_CANCLED, headers={}, data={})
    return json.loads(response.text)

def get_pnrs(flight_id):
    response = requests.request("GET", HOST + API_PNR_RANKING + str(flight_id), headers={}, data={})
    return json.loads(response.text)

def get_alt_flights(flight_id):
    response = requests.request("GET", HOST + API_ALT_FLIGHT + str(flight_id), headers={}, data={})
    return json.loads(response.text)

if __name__ == "__main__":
    # print(get_cancled())
    print(get_alt_flights('32f010f1'))
