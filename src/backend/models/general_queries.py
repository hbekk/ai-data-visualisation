from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pymongo import MongoClient, ASCENDING
from .database import collection as Telemetry
import json

@lru_cache(maxsize=50)  
def fetch_sensor_values(start_date, end_date, sensor_name, asset_id, limit=None):
    try:
        query = {
            "metadata.name": {"$regex": f"^{sensor_name}$", "$options": "i"},
            "metadata.asset_id": asset_id  
        }
        
        if start_date:
            date_range = {"$gte": datetime.strptime(start_date, "%Y-%m-%d")}
            if end_date and start_date != end_date:
                date_range["$lt"] = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            else:
                date_range["$lt"] = date_range["$gte"] + timedelta(days=1)

            query["timestamp"] = date_range

        print(f"\nDEBUG: Running MongoDB query:\n{query}")

        cursor = Telemetry.find(query, {"timestamp": 1, "metadata.name": 1, "value": 1, "_id": 0})
        results = list(cursor)

        if not results:
            return {"error": f"Sorry, no {sensor_name} data was found for {start_date}."}

        values = [(doc["timestamp"], doc["value"]) for doc in results if isinstance(doc.get("value"), (int, float))
                  and "timestamp" in doc]  

        return values

    except Exception as e:
        return {"error": str(e)}
    



# Work in progress
def fetch_embedded_queries(user_query):
  
    query_doc = db.queries.find_one({"natural_query": user_query})

    if not query_doc:
        print(f"DEBUG: No matching query found for '{user_query}'")
        return {"error": "No matching query found in the database."}

    print(f"DEBUG: Found stored query in 'queries' collection:\n{query_doc}")

    mongo_query = query_doc.get("mongo_query")

    if not mongo_query:
        print("DEBUG: Stored query is missing the MongoDB query structure.")
        return {"error"}

    print(f"DEBUG: Extracted MongoDB Query:\n{mongo_query}")

    try:
        if isinstance(mongo_query, str):
            mongo_query = json.loads(mongo_query.replace("'", '"'))  

        if "timestamp" in mongo_query:
            if "$gte" in mongo_query["timestamp"]:
                mongo_query["timestamp"]["$gte"] = datetime.strptime(
                    mongo_query["timestamp"]["$gte"]["$date"], "%Y-%m-%dT%H:%M:%SZ"
                )
            if "$lt" in mongo_query["timestamp"]:
                mongo_query["timestamp"]["$lt"] = datetime.strptime(
                    mongo_query["timestamp"]["$lt"]["$date"], "%Y-%m-%dT%H:%M:%SZ"
                )

        if "metadata.name" in mongo_query:
            mongo_query["metadata.name"] = {"$regex": f"^{mongo_query['metadata.name']}$", "$options": "i"}

    except Exception as e:
        print(f"DEBUG: Error parsing query: {e}")
        return {"error": f"Invalid stored query format: {e}"}

    print(f"DEBUG: Final Query to Execute:\n{mongo_query}")

    try:
        results = list(db.Telemetry.find(mongo_query, {"_id": 0, "timestamp": 1, "metadata.name": 1, "value": 1}))

        print(f"DEBUG: Query executed successfully, found {len(results)} results.")

        if not results:
            return {"error": f"No data found for query: {user_query}"}

        return results
    
    except Exception as e:
        print(f"DEBUG: MongoDB Query Execution Error: {e}")
        return {"error": f"MongoDB execution error: {e}"}

