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
- Run the `flight/management/data/generate.ipynb` to generate some `csv`

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
    python3 manage.py populate_basic
    ```
    - For table cleanup use
    ```python3
    python3 manage.py populate_basic --clean
    ```

- Table : `Aircraft`
    - model : `Aircraft`
    - command:
     ```python3
    python3 manage.py populate_aircraft --clean
    ```  

- Table : `Flight`, `FlightScheduleDate`, `FlightSchedule`
    - model : `Flight`, `FlightScheduleDate`, `FlightSchedule`
    - command: 
    ```python3
    python3 manage.py populate_flight --clean
    ```
 
- Table : `PNR`, `PnrFlightMapping`, `PnrPassenger`
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

### Shortcut (using the provided data)
- Make sure to have the provided data in the `flight/management/data/` directory in `csv` format namely,
    - `flight_inventory_table.csv`
    - `passenger_table.csv`
    - `schedule_table.csv`
- Run the `flight/management/data/generate_basics.ipynb` and then the `flight/management/data/generate.ipynb` to generate necessary `csv` files to be saved in `flight/management/data/` directory namely,
    - `aircrafts.csv`
    - `cabin.csv`
    - `carrier.csv`
    - `class.csv`
    - `group.csv`
    - `ssr.csv`
    - `seat-distribution.csv`
- After above steps, run,
    ```
    python3 manage.py load_data
    ```
    which is the shortcut to load the mentioned tables in the dataset if we have the given dataset


### Note
- for data ingestion use this order, first airports, then basic, routes, then pnr
- data ingestion, except for the shortcut method, generates synthetic data
- shortcut method uses the provided data to populate the dataset


# API Endpoints
- `\canclled`
    - Returns the list of cancelled flights and their count
    - Method: `GET`
    - Filters by status = `Cancelled`
    - Sample Response:
    ```json
    {
    "count": 3,
        "data": [
            {
                "flight_id": "INV-ZZ-9430442",
                "departure_airport": "DEL",
                "arrival_airport": "AMD",
                "status": "Cancelled",
                "arrival_time": "2024-05-31T18:49:00Z",
                "departure_time": "2024-05-31T17:18:00Z"
            },
            {
                "flight_id": "INV-ZZ-6235385",
                "departure_airport": "BLR",
                "arrival_airport": "CCU",
                "status": "Cancelled",
                "arrival_time": "2024-04-24T12:24:00Z",
                "departure_time": "2024-04-24T09:42:00Z"
            },
            {
                "flight_id": "INV-ZZ-6129434",
                "departure_airport": "GAU",
                "arrival_airport": "PNQ",
                "status": "Cancelled",
                "arrival_time": "2024-06-17T23:20:00Z",
                "departure_time": "2024-06-17T10:04:00Z"
            }
        ]
    }
    ```
- `\pnr_ranking?flight_id={id}`
    - Returns the list of PNRs in the flight with the given flight_id
    - Method: `GET`
    - Filters by flight_id
    - Sample Response:
    ```json
    {
        "data": [
            {
                "pnr": "EUTS74",
                "score": 16800,
                "class": "E",
                "pax": 9
            },
            {
                "pnr": "LLEF53",
                "score": 14100,
                "class": "E",
                "pax": 6
            },
            {
                "pnr": "QVZR28",
                "score": 9000,
                "class": "P",
                "pax": 6
            }
        ]
    }
    ```

- `\alt_flight?flight_id={id}`
    - Returns the list of alternative flights for the given flight_id, both direct and connecting
    - Method: `GET`
    - Filters by flight_id and status = `Scheduled`
    - Sample Response:
    ```json
    {
        "data": [
            {
                "flight_id": "INV-ZZ-5198628",
                "departure_airport": "AMD",
                "arrival_airport": "DEL",
                "status": "Scheduled",
                "arrival_time": "2024-06-01T01:14:00Z",
                "departure_time": "2024-05-31T19:17:00Z",
                "total_avilable_seats": 114,
                "delay": "1:59:00",
                "flight_time": "5:57:00",
                "avilable_seats": {
                    "C": 40,
                    "R": 60,
                    "E": 14,
                    "F": 0
                },
                "n_score": 0
            },
            {
                "flight_id": "INV-ZZ-9779199",
                "departure_airport": "AMD",
                "arrival_airport": "DEL",
                "status": "Scheduled",
                "arrival_time": "2024-06-03T01:14:00Z",
                "departure_time": "2024-06-02T19:17:00Z",
                "total_avilable_seats": 113,
                "delay": "2 days, 1:59:00",
                "flight_time": "5:57:00",
                "avilable_seats": {
                    "C": 40,
                    "R": 60,
                    "E": 13,
                    "F": 0
                },
                "n_score": 0
            }
        ],
        "r_flights": [
            {
                "flight_id": "INV-ZZ-9430442",
                "departure_airport": "DEL",
                "arrival_airport": "AMD",
                "status": "Cancelled",
                "arrival_time": "2024-05-31T18:49:00Z",
                "departure_time": "2024-05-31T17:18:00Z"
            }
        ],
        "c_flights": [],
        "t_flights": [
            [
                {
                    "flight_id": "INV-ZZ-8966591",
                    "departure_airport": "DEL",
                    "arrival_airport": "BOM",
                    "status": "Scheduled",
                    "arrival_time": "2024-05-31T23:15:00Z",
                    "departure_time": "2024-05-31T18:24:00Z",
                    "total_avilable_seats": 119,
                    "delay": "1:06:00",
                    "flight_time": "4:51:00",
                    "avilable_seats": {
                        "C": 44,
                        "R": 67,
                        "E": 8,
                        "F": 0
                    }
                },
                {
                    "flight_id": "INV-ZZ-2637912",
                    "departure_airport": "BOM",
                    "arrival_airport": "MAA",
                    "status": "Scheduled",
                    "arrival_time": "2024-06-01T07:45:00Z",
                    "departure_time": "2024-06-01T04:39:00Z",
                    "total_avilable_seats": 167,
                    "delay": "5:24:00",
                    "flight_time": "3:06:00",
                    "avilable_seats": {
                        "C": 54,
                        "R": 80,
                        "E": 33,
                        "F": 0
                    }
                }
            ],
            [
                {
                    "flight_id": "INV-ZZ-8966591",
                    "departure_airport": "DEL",
                    "arrival_airport": "BOM",
                    "status": "Scheduled",
                    "arrival_time": "2024-05-31T23:15:00Z",
                    "departure_time": "2024-05-31T18:24:00Z",
                    "total_avilable_seats": 119,
                    "delay": "1:06:00",
                    "flight_time": "4:51:00",
                    "avilable_seats": {
                        "C": 44,
                        "R": 67,
                        "E": 8,
                        "F": 0
                    }
                },
                {
                    "flight_id": "INV-ZZ-7125734",
                    "departure_airport": "BOM",
                    "arrival_airport": "MAA",
                    "status": "Scheduled",
                    "arrival_time": "2024-06-02T07:45:00Z",
                    "departure_time": "2024-06-02T04:39:00Z",
                    "total_avilable_seats": 181,
                    "delay": "1 day, 5:24:00",
                    "flight_time": "3:06:00",
                    "avilable_seats": {
                        "C": 54,
                        "R": 80,
                        "E": 39,
                        "F": 8
                    }
                },
            ]
        ]
    }
    ```