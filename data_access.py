data_access.py
----------------
Handles all persistence for the Fuel Consumption Analysis System.
 
Responsibilities (kept separate from analysis.py so that storage
details can change - e.g. CSV to a database - without touching any
of the calculation logic):
    * Registering / loading vehicles          -> vehicles.csv
    * Logging / loading trips                 -> trips.csv
    * Basic duplicate / existence checks using a set of vehicle numbers
"""
 
import csv
import os
 
VEHICLE_FILE = "vehicles.csv"
TRIP_FILE = "trips.csv"
 
VEHICLE_FIELDS = ["vehicle_no", "make", "model", "initial_odometer"]
TRIP_FIELDS = ["vehicle_no", "date", "distance_km", "fuel_litres",
               "odometer", "fuel_price_per_litre"]
 
 
def _ensure_file(path, fieldnames):
    """Create the CSV file with a header row if it does not exist yet."""
    if not os.path.exists(path):
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
 
 
def load_vehicles():
    """Return vehicles as a dict keyed by vehicle_no (registration number).
 
    dict is used here because a vehicle number is a natural unique key and
    O(1) look-up is required every time a trip is logged against it.
    """
    _ensure_file(VEHICLE_FILE, VEHICLE_FIELDS)
    vehicles = {}
    with open(VEHICLE_FILE, newline="") as f:
        for row in csv.DictReader(f):
            row["initial_odometer"] = float(row["initial_odometer"])
            vehicles[row["vehicle_no"]] = row
    return vehicles
 
 
def save_vehicle(vehicle_no, make, model, initial_odometer):
    """Append one vehicle record to vehicles.csv."""
    _ensure_file(VEHICLE_FILE, VEHICLE_FIELDS)
    with open(VEHICLE_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=VEHICLE_FIELDS)
        writer.writerow({
            "vehicle_no": vehicle_no,
            "make": make,
            "model": model,
            "initial_odometer": initial_odometer,
        })
 
 
def load_trips():
    """Return all trips as a list of dicts (order of logging preserved)."""
    _ensure_file(TRIP_FILE, TRIP_FIELDS)
    trips = []
    with open(TRIP_FILE, newline="") as f:
        for row in csv.DictReader(f):
            row["distance_km"] = float(row["distance_km"])
            row["fuel_litres"] = float(row["fuel_litres"])
            row["odometer"] = float(row["odometer"])
            row["fuel_price_per_litre"] = float(row["fuel_price_per_litre"])
            trips.append(row)
    return trips
 
 
def save_trip(vehicle_no, date, distance_km, fuel_litres, odometer, price):
    """Append one trip record to trips.csv."""
    _ensure_file(TRIP_FILE, TRIP_FIELDS)
    with open(TRIP_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TRIP_FIELDS)
        writer.writerow({
            "vehicle_no": vehicle_no,
            "date": date,
            "distance_km": distance_km,
            "fuel_litres": fuel_litres,
            "odometer": odometer,
            "fuel_price_per_litre": price,
        })
 
 
def registered_vehicle_numbers():
    """Return a *set* of vehicle numbers already registered.
 
    A set is used purely for fast membership testing (`in`) when
    validating new registrations / trip entries against duplicates.
    """
    return set(load_vehicles().keys())
