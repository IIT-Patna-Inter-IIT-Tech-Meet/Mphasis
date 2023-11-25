# Data Ingestion
- Table : `airport`
    - source : `flight/management/commands/in-airport.csv`
    - model : Airport
    - table_name: `flight_airport`
    - command: `python3 manage.py populate --filename flight/management/data/in-airports.csv --delete`
- 