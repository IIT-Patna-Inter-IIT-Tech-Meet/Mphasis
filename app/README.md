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
- Table : `airline`