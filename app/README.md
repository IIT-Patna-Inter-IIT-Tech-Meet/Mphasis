# How to run ? 
- Activate virtual environment
    ```python3
    source venv/bin/activate
    ```
- Install requirements
    ```python3
    pip3 install -r requirements.txt
    ```
- Make sure to migrate first
    ```
    python3 manage.py migrate
    ```
- Replace the db.sqlite3 with the one in the drive
- Run the server
    ```
    python3 manage.py runserver
    ```


# Data Ingestion
- Table : `airport`
    - source : `flight/management/commands/in-airport.csv`
    - model : Airport
    - table_name: `flight_airport`
    - command: 
    ```python3
    python3 manage.py populate --filename flight/management/data/in-airports.csv --delete
    ```
- Table : `Cabin Types`, `Class Types`, `SSRs`, `Groups`
    - source : 
        - `flight/management/commands/in-cabin.csv`, 
        - `flight/management/commands/in-class.csv`, 
        - `flight/management/commands/in-ssr.csv`, 
        - `flight/management/commands/in-group.csv`
    - model : Cabin, Class, SSR, Group
    - table_name: `flight_cabin`, `flight_class`, `flight_ssr`, `flight_group`
    - command: 
    ```python3
    python3 manage.py populate_baic
    ```
    - For table cleanup use
    ```python3
    python3 manage.py populate_baic --clean
    ```
- Table : `PNR`, `FlightPnrMapping`
    - model : PNR, FlightPnrMapping
    - table_name: `flight_pnr`, `flight_flightpnrmapping`
    - command: 
    ```python3
    python3 manage.py populate_pnr
    ```
    - For table cleanup use
    ```python3
    python3 manage.py populate_pnr --clean
    ```

### Note
for data ingestion use this order, first airports, then basic, routes, then pnr


# API Endpoints
- `\canclled`
    - Returns the list of cancelled flights
    - Method: `GET`
    - Filters by status = `red`
    - Sample Response:
    ```json
    {
    "data": [
        {
            "flight_id": "32f010f1",
            "flight_number": "SG385",
            "departure_airport": "BOM",
            "arrival_airport": "GOP",
            "status": "red",
            "aircraft": "VT-SYZ",
            "owner": "SpiceJet",
            "arrival_time": "2023-11-23T05:30:00Z",
            "departure_time": "2023-11-23T02:55:00Z"
        },
        {
            "flight_id": "32ede872",
            "flight_number": "6E7064",
            "departure_airport": "TIR",
            "arrival_airport": "VTZ",
            "status": "red",
            "aircraft": "VT-IXZ",
            "owner": "IndiGo",
            "arrival_time": "2023-11-22T13:25:00Z",
            "departure_time": "2023-11-22T11:55:00Z"
        },
    ]
    }
    ```
- `\pnr_ranking?flight_id={id}`
    - Returns the list of passengers in the flight with the given flight_id
    - Method: `GET`
    - Filters by flight_id
    - Sample Response:
    ```json
    {
    "data": [
        {
            "pnr": "40d50d",
            "score": 1600,
            "class": "F",
            "pax": 2
        },
        {
            "pnr": "825a3b",
            "score": 1350,
            "class": "O",
            "pax": 3
        },
    ]
    }
    ```

- `\alt_flight?flight_id={id}`
    - Returns the list of alternative flights for the given flight_id
    - Method: `GET`
    - Filters by flight_id and status = `green`
    - Sample Response:
    ```json
    {
    "data": [
        {
            "flight_id": "32eff78f",
            "flight_number": "QP1524",
            "departure_airport": "BOM",
            "arrival_airport": "LKO",
            "status": "green",
            "arrival_time": "2023-11-23T05:30:00Z",
            "departure_time": "2023-11-23T03:15:00Z",
            "all_seats": {
                "Z": 54,
                "T": 88
            },
            "booked_seats": {
                "T": 54,
                "Z": 33
            }
        },
        {
            "flight_id": "32f02e1e",
            "flight_number": "6E5316",
            "departure_airport": "BOM",
            "arrival_airport": "AGR",
            "status": "green",
            "arrival_time": "2023-11-23T07:40:00Z",
            "departure_time": "2023-11-23T05:25:00Z",
            "all_seats": {
                "T": 74,
                "A": 8,
                "N": 72,
                "O": 102
            },
            "booked_seats": {
                "A": 5,
                "N": 57,
                "O": 63,
                "T": 48
            }
        },
    ]
    }
    ```