main.py
--------
Menu-driven console application for the Fuel Consumption Analysis
System. Ties together the data_access (persistence) and analysis
(computation) modules/packages.
"""
 
import re
from datetime import datetime
 
import data_access
import analysis
 
VEHICLE_NO_PATTERN = re.compile(r"^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$")
 
 
# ---------------------------------------------------------------------
# String-handling / input-validation helpers
# ---------------------------------------------------------------------
def clean_vehicle_no(raw):
    """Normalise a vehicle registration number: strip spaces, upper-case."""
    return raw.strip().upper().replace(" ", "")
 
 
def is_valid_vehicle_no(vehicle_no):
    return bool(VEHICLE_NO_PATTERN.match(vehicle_no))
 
 
def is_valid_date(raw):
    try:
        datetime.strptime(raw.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False
 
 
def read_positive_float(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value < 0:
                print("  Value cannot be negative. Try again.")
                continue
            return value
        except ValueError:
            print("  Please enter a valid number.")
 
 
# ---------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------
def register_vehicle():
    print("\n-- Register Vehicle --")
    raw_no = input("Vehicle number (e.g. TN22AB1234): ")
    vehicle_no = clean_vehicle_no(raw_no)
    if not is_valid_vehicle_no(vehicle_no):
        print("  Invalid format. Expected e.g. TN22AB1234.")
        return
    existing = data_access.registered_vehicle_numbers()
    if vehicle_no in existing:
        print(f"  Vehicle {vehicle_no} is already registered.")
        return
    make = input("Make (e.g. Honda): ").strip().title()
    model = input("Model (e.g. Activa): ").strip().title()
    odometer = read_positive_float("Current odometer reading (km): ")
    data_access.save_vehicle(vehicle_no, make, model, odometer)
    print(f"  Vehicle {vehicle_no} registered successfully.")
 
 
def log_trip():
    print("\n-- Log Trip / Refuelling --")
    vehicle_no = clean_vehicle_no(input("Vehicle number: "))
    if vehicle_no not in data_access.registered_vehicle_numbers():
        print("  Vehicle not found. Please register it first.")
        return
    date = input("Date (YYYY-MM-DD): ").strip()
    if not is_valid_date(date):
        print("  Invalid date format.")
        return
    distance = read_positive_float("Distance travelled since last fill (km): ")
    fuel = read_positive_float("Fuel filled (litres): ")
    odometer = read_positive_float("Current odometer reading (km): ")
    price = read_positive_float("Fuel price per litre (Rs.): ")
    data_access.save_trip(vehicle_no, date, distance, fuel, odometer, price)
    kmpl = analysis.trip_mileage_kmpl(
        {"distance_km": distance, "fuel_litres": fuel})
    print(f"  Trip logged. This trip's mileage: {kmpl} km/l")
 
 
def view_vehicle_summary():
    print("\n-- Vehicle Summary --")
    vehicle_no = clean_vehicle_no(input("Vehicle number: "))
    trips = analysis.group_trips_by_vehicle(data_access.load_trips())
    if vehicle_no not in trips:
        print("  No trips logged for this vehicle yet.")
        return
    summary = analysis.vehicle_summary(vehicle_no, trips[vehicle_no])
    _print_summary(summary)
 
 
def _print_summary(summary):
    print(f"  Vehicle           : {summary['vehicle_no']}")
    print(f"  Trips logged      : {summary['trip_count']}")
    print(f"  Total distance    : {summary['total_distance_km']} km")
    print(f"  Total fuel used   : {summary['total_fuel_litres']} L")
    print(f"  Overall mileage   : {summary['overall_mileage_kmpl']} km/l")
    print(f"  Total fuel cost   : Rs. {summary['total_cost']}")
    print("  Monthly consumption:")
    for month, litres in sorted(summary["monthly_consumption"].items()):
        print(f"      {month}: {round(litres, 2)} L")
 
 
def generate_report():
    print("\n-- Consolidated Fleet Report --")
    trips = data_access.load_trips()
    if not trips:
        print("  No trip data available yet.")
        return
    report = analysis.consolidated_report(trips)
 
    print("\n  Efficiency Ranking (best to worst):")
    for rank, s in enumerate(report["ranking"], start=1):
        print(f"   {rank}. {s['vehicle_no']:10s} "
              f"{s['overall_mileage_kmpl']:6.2f} km/l "
              f"(distance {s['total_distance_km']} km, "
              f"fuel {s['total_fuel_litres']} L)")
 
    if report["most_efficient"]:
        print(f"\n  Most efficient : {report['most_efficient']['vehicle_no']} "
              f"({report['most_efficient']['overall_mileage_kmpl']} km/l)")
        print(f"  Least efficient: {report['least_efficient']['vehicle_no']} "
              f"({report['least_efficient']['overall_mileage_kmpl']} km/l)")
 
    print("\n  Flagged trips (abnormally high consumption):")
    if not report["anomalies"]:
        print("   None detected.")
    for a in report["anomalies"]:
        print(f"   {a['vehicle_no']} on {a['date']}: "
              f"{a['litres_per_100km']} L/100km "
              f"(vehicle avg {a['vehicle_avg_l_per_100km']} L/100km)")
 
 
def print_menu():
    print("\n===== Fuel Consumption Analysis System =====")
    print("1. Register Vehicle")
    print("2. Log Trip / Refuelling")
    print("3. View Vehicle Summary")
    print("4. Generate Consolidated Report")
    print("5. Exit")
 
 
def main():
    actions = {
        "1": register_vehicle,
        "2": log_trip,
        "3": view_vehicle_summary,
        "4": generate_report,
    }
    while True:
        print_menu()
        choice = input("Enter choice (1-5): ").strip()
        if choice == "5":
            print("Exiting. Data has been saved to vehicles.csv / trips.csv.")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("  Invalid choice, please enter a number from 1 to 5.")
 
 
if __name__ == "__main__":
    main()
 
