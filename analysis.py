analysis.py
------------
Pure computation layer for the Fuel Consumption Analysis System.
Contains no file I/O - every function takes in-memory data structures
(produced by data_access.py) and returns computed results, which keeps
the logic easy to unit-test in isolation.
"""
 
from collections import defaultdict
 
# A trip is flagged as abnormal if its litres-per-100km figure exceeds
# the vehicle's own average by more than this factor.
ANOMALY_THRESHOLD_FACTOR = 1.5
 
 
def group_trips_by_vehicle(trips):
    """Group trip dicts by vehicle_no.
 
    Returns: dict[str, list[dict]]
    """
    grouped = defaultdict(list)
    for trip in trips:
        grouped[trip["vehicle_no"]].append(trip)
    return grouped
 
 
def trip_mileage_kmpl(trip):
    """Return km-per-litre for a single trip (tuple-based intermediate).
 
    A (distance, fuel) tuple is used to keep the two related quantities
    bound together immutably while the ratio is derived.
    """
    distance, fuel = (trip["distance_km"], trip["fuel_litres"])
    if fuel <= 0:
        return 0.0
    return round(distance / fuel, 2)
 
 
def vehicle_summary(vehicle_no, trips_for_vehicle):
    """Compute mileage, total distance/fuel/cost and monthly consumption
    for one vehicle.
 
    Returns a dict summary; monthly consumption is a dict keyed by
    'YYYY-MM' (derived from each trip's date) -> total litres consumed
    that month, since a dict is the natural structure for a group-by-key
    aggregation.
    """
    total_distance = sum(t["distance_km"] for t in trips_for_vehicle)
    total_fuel = sum(t["fuel_litres"] for t in trips_for_vehicle)
    total_cost = sum(t["fuel_litres"] * t["fuel_price_per_litre"]
                      for t in trips_for_vehicle)
 
    monthly_consumption = defaultdict(float)
    for t in trips_for_vehicle:
        month_key = t["date"][:7]  # 'YYYY-MM-DD' -> 'YYYY-MM'
        monthly_consumption[month_key] += t["fuel_litres"]
 
    overall_mileage = round(total_distance / total_fuel, 2) if total_fuel else 0.0
 
    return {
        "vehicle_no": vehicle_no,
        "trip_count": len(trips_for_vehicle),
        "total_distance_km": round(total_distance, 2),
        "total_fuel_litres": round(total_fuel, 2),
        "total_cost": round(total_cost, 2),
        "overall_mileage_kmpl": overall_mileage,
        "monthly_consumption": dict(monthly_consumption),
    }
 
 
def rank_vehicles_by_efficiency(trips):
    """Return vehicles sorted from most to least fuel-efficient
    (highest km/l first) as a list of summary dicts.
    """
    grouped = group_trips_by_vehicle(trips)
    summaries = [vehicle_summary(v, t) for v, t in grouped.items()]
    return sorted(summaries, key=lambda s: s["overall_mileage_kmpl"], reverse=True)
 
 
def flag_abnormal_trips(trips):
    """Return trips whose fuel usage per 100 km is well above that
    vehicle's own average - i.e. likely data-entry errors or genuinely
    wasteful trips worth investigating.
    """
    grouped = group_trips_by_vehicle(trips)
    flagged = []
    for vehicle_no, vtrips in grouped.items():
        # litres per 100 km for every trip of this vehicle
        rates = []
        for t in vtrips:
            if t["distance_km"] > 0:
                rates.append(t["fuel_litres"] / t["distance_km"] * 100)
            else:
                rates.append(0)
        if not rates:
            continue
        avg_rate = sum(rates) / len(rates)
        for t, rate in zip(vtrips, rates):
            if avg_rate > 0 and rate > avg_rate * ANOMALY_THRESHOLD_FACTOR:
                flagged.append({**t, "litres_per_100km": round(rate, 2),
                                 "vehicle_avg_l_per_100km": round(avg_rate, 2)})
    return flagged
 
 
def deduplicate_trips(trips):
    """Remove exact-duplicate trip entries (same vehicle, date, distance,
    fuel and odometer) using a set of tuples for O(1) duplicate checks.
    """
    seen = set()
    unique_trips = []
    for t in trips:
        key = (t["vehicle_no"], t["date"], t["distance_km"],
               t["fuel_litres"], t["odometer"])
        if key not in seen:
            seen.add(key)
            unique_trips.append(t)
    return unique_trips
 
 
def consolidated_report(trips):
    """Build the final consolidated report combining ranking and
    anomaly detection - this is what the menu's 'Generate Report'
    option calls.
    """
    clean_trips = deduplicate_trips(trips)
    ranking = rank_vehicles_by_efficiency(clean_trips)
    anomalies = flag_abnormal_trips(clean_trips)
    return {
        "ranking": ranking,
        "most_efficient": ranking[0] if ranking else None,
        "least_efficient": ranking[-1] if ranking else None,
        "anomalies": anomalies,
    }
 
