#!/usr/bin/fish

#activate virtualenv
source ../venv/bin/activate.fish

# migrate and flash
python3 manage.py makemigrations 
python3 manage.py migrate
python3 manage.py flush --no-input

#run script
python3 manage.py populate_airport --clean
python3 manage.py populate_basic --clean
python3 manage.py populate_aircraft --clean
python3 manage.py populate_flight --clean
python3 manage.py populate_pnr --clean