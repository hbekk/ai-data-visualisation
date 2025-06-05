from datetime import datetime, timezone
from pymongo import ASCENDING
from models.database import collection as Telemetry

#UTILITY FUNCTIONS
def parse_iso_to_utc(iso_str):
    return datetime.fromisoformat(iso_str.replace("Z", "+00:00")).astimezone(timezone.utc)

def inject_asset_id(query, asset_id):
    if isinstance(query, dict):
        query["metadata.asset_id"] = asset_id
    elif isinstance(query, list):
        for stage in query:
            if "$match" in stage:
                stage["$match"]["metadata.asset_id"] = asset_id
                break
    return query

def unwrap_query(raw):
    if isinstance(raw, dict) and "query" in raw:
        return raw["query"]
    return raw

def clean_query_timestamps(query):
    if isinstance(query, dict) and "timestamp" in query:
        if "$gte" in query["timestamp"] and isinstance(query["timestamp"]["$gte"], str):
            query["timestamp"]["$gte"] = parse_iso_to_utc(query["timestamp"]["$gte"])
        if "$lt" in query["timestamp"] and isinstance(query["timestamp"]["$lt"], str):
            query["timestamp"]["$lt"] = parse_iso_to_utc(query["timestamp"]["$lt"])
    return query


#MONGO EXECUTIION

def execute_pie_chart_query(query):
    print("Executing pie chart.")
    for stage in query:
        if "$match" in stage and "timestamp" in stage["$match"]:
            ts = stage["$match"]["timestamp"]
            if "$gte" in ts and isinstance(ts["$gte"], str):
                ts["$gte"] = parse_iso_to_utc(ts["$gte"])
            if "$lt" in ts and isinstance(ts["$lt"], str):
                ts["$lt"] = parse_iso_to_utc(ts["$lt"])

    try:
        results = list(Telemetry.aggregate(query))
    except Exception as e:
        return {"error": "Aggregation query execution failed."}

    if not results:
        return {"error": "No distribution data available."}


    patched_results = []
    for r in results:
        if isinstance(r.get("_id"), dict) and {"date", "sensor"}.issubset(r["_id"]):
            date_str = r["_id"]["date"]  
            sensor = r["_id"]["sensor"]
            timestamp = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            patched_results.append({
            "timestamp": timestamp,
            "value": r.get("averageValue"),
            "metadata": {"name": sensor}
        })
            continue
        elif isinstance(r.get("_id"), dict) and {"hour", "sensor"}.issubset(r["_id"]):
            hour = r["_id"]["hour"]
            sensor = r["_id"]["sensor"]
            date = query[0]["$match"]["timestamp"]["$gte"].date()
            timestamp = datetime(year=date.year, month=date.month, day=date.day, hour=hour, tzinfo=timezone.utc)
            patched_results.append({
                "timestamp": timestamp,
                "value": r.get("avgValue") or r.get("averageValue"),
                "metadata": {"name": sensor}
            })
        else:
            patched_results.append({
            "_id": str(r.get("_id", "Unknown")),
            "count": r.get("count", 0),
            "metadata": {
            "name": query[0].get("$match", {}).get("metadata.name", "Unknown Sensor")
                }
            })

    return patched_results
    


def execute_query(query, asset_id):
    query = unwrap_query(query)
    
    if not isinstance(query, (dict, list)):
        return {"error": "Invalid query format"}

    if isinstance(query, list) and any("$group" in step for step in query):
        return execute_pie_chart_query(query)

    query = clean_query_timestamps(query)
    query = inject_asset_id(query, asset_id)

    if isinstance(query, dict) and "metadata" in query and isinstance(query["metadata"], dict):
        if "name" in query["metadata"]:
            query["metadata.name"] = query["metadata"]["name"]
            del query["metadata"]
        elif "$in" in query["metadata"]:
            query["metadata.name"] = query["metadata"]
            del query["metadata"]


    sort_field = query.pop("sort", None) if isinstance(query, dict) else None

    try:
        print(f"Executing MongoDB Query:\n{query}")
        if sort_field and isinstance(sort_field, dict):
            results = list(Telemetry.find(query).sort([(k, v) for k, v in sort_field.items()]))
        else:
            results = list(Telemetry.find(query))
    except Exception as e:
        return {"error": "MongoDB query execution failed."}

    if not results:
        return {"success": False, "message": "No data matches your request. Try a new timeframe or sensor."}


    print(f"Has {len(results)} records.")
    return results

def execute_queries(filled_queries, asset_id):
    if not isinstance(filled_queries, list):
        return {"error": "Invalid query format"}

    results = []

    for raw in filled_queries:
        query = unwrap_query(raw)
        query = inject_asset_id(query, asset_id)
        query_results = execute_query(query, asset_id)


        if isinstance(query_results, dict) and (query_results.get("error") or query_results.get("success") is False):
            return query_results

        if isinstance(query_results, list):
            results.extend(query_results)

    if not results:
        return {"success": False, "message": "No data matches your request. Try a new timeframe or sensor."}

    return results

