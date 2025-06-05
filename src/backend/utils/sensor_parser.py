from models.database import collection as Telemetry
from datetime import datetime, timedelta
import re

SENSOR_NAMES_CACHE = None

def generate_keywords(sensor_name):
    variations = [
        sensor_name.lower(),
        sensor_name.replace(" ", ""),
        sensor_name.replace(" ", "").lower()
    ]
    
    return variations


def get_sensor_types():
    global SENSOR_NAMES_CACHE
    
    if SENSOR_NAMES_CACHE is None:
        print("INFO: Loading sensor names from database (lazy loading)...")
        SENSOR_NAMES_CACHE = list(Telemetry.distinct("metadata.name"))
        print(f"INFO: Loaded {len(SENSOR_NAMES_CACHE)} sensor names.")
        
        if SENSOR_NAMES_CACHE:
            print(f"DEBUG: First few sensors: {SENSOR_NAMES_CACHE[:5]}")
        else:
            print("WARNING: No sensor names found in database")
    
    return SENSOR_NAMES_CACHE

def get_recent_sensors(asset_id: str, days: int = 14, limit: int = 10) -> list[str]:
    cutoff = datetime.utcnow() - timedelta(days=days)
    pipeline = [
        {"$match": {"asset_id": asset_id, "timestamp": {"$gte": cutoff}}},
        {"$group": {"_id": "$metadata.name", "latest": {"$max": "$timestamp"}}},
        {"$sort": {"latest": -1}},
        {"$limit": limit}
     ]
    results = list(Telemetry.aggregate(pipeline))
    return [r["_id"] for r in results]


def extract_sensor(query_text):
    query_text = query_text.lower().strip()

    sensor_types = get_sensor_types()
    
    sensor_keywords_map = {}
    detected_sensors = []

    for sensor in sensor_types:
        sensor_keywords_map[sensor] = generate_keywords(sensor)
    
    for sensor, keywords in sensor_keywords_map.items():
        if any(keyword in query_text for keyword in keywords):
            detected_sensors.append(sensor)
            if "distribution" in query_text or "pie chart" in query_text:
                print(f"INFO: Detected request for pie chart for sensor: {sensor}")
    
    if "distribution" in query_text or "sensor types" in query_text or "pie chart" in query_text:
        print("INFO: Detected request for a pie chart of all sensors. Fetching sensor types from DB.")
        if not sensor_types:
            print("ERROR: No sensor types found in the database.")
            return {"error": "No sensor types found."}
        return sensor_types  

    if len(detected_sensors) == 1 and any(w in query_text for w in ["vs", "and", "with", "compared to"]):
        base = detected_sensors[0].rsplit(" ", 1)[0]  
        variations = [f"{base} in", f"{base} out", f"{base} reg"]
        expanded = [s for s in variations if s in sensor_types and s not in detected_sensors]
        if expanded:
            print(f"INFO: Expanded sensor match from '{detected_sensors[0]}' to {detected_sensors + expanded}")
            detected_sensors.extend(expanded)

    if not detected_sensors:
        return {"error": "Unknown sensor type."}

    return detected_sensors

