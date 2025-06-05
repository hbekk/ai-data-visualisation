from .database import chart_archive_collection as collection
from .database import chart_history_collection
import json
from pymongo.errors import PyMongoError
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel


def addArchivedChart(chart_data: str):
    try:
        chart_dict = json.loads(chart_data)
        
        result = collection.insert_one(chart_dict)
        print(f"Chart archived successfully with ID: {result.inserted_id}")
    
    except json.JSONDecodeError:
        print("Failed to decode JSON. Please check the format of chart_data.")
    except PyMongoError as e:
        print(f"MongoDB error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def get_chart_data(asset_id):
    try:
        charts = collection.find({"asset_id": asset_id})  
        charts_list = list(charts)  
        
        for chart in charts_list:
            chart["_id"] = str(chart["_id"])
        
        return charts_list 
        
    except Exception as e:
        return {"error": str(e)} 

def remove_saved_data(timestamp):
    try:
        collection.delete_one({"date": timestamp})
    except PyMongoError as e:
        print(f"MongoDB error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



### CHART HISTORY

def addChartHistory(chart_data):
    try:
        chart_dict = chart_data
        result = chart_history_collection.insert_one(chart_dict)
        print(f"Chart archived successfully with ID: {result.inserted_id}")
        asset_id = chart_dict['asset_id']
        count = chart_history_collection.count_documents({"asset_id": asset_id})
        print(f"Total charts for asset_id {asset_id}: {count}")

        if count > 50:
            excess = count - 50
            oldest_entries = chart_history_collection.find({"asset_id": asset_id}).sort("date", 1).limit(excess)
            
            ids_to_delete = [entry["_id"] for entry in oldest_entries]
            print(f"Excess entries to delete: {ids_to_delete}")

            if ids_to_delete:
                result = chart_history_collection.delete_many({"_id": {"$in": ids_to_delete}})
                print(f"Deleted {result.deleted_count} excess charts.")

    except json.JSONDecodeError:
        print("Failed to decode JSON. Please check the format of chart_data.")
    except PyMongoError as e:
        print(f"MongoDB error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def get_chart_history(asset_id):
    try:
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        seven_days_ago_ms = int(seven_days_ago.timestamp() * 1000)

        print(seven_days_ago_ms)

        chart_history_collection.delete_many({
            "asset_id": asset_id,
            "date": {"$lt": seven_days_ago_ms}
        })

        charts = chart_history_collection.find({"asset_id": asset_id})  
        charts_list = list(charts)  
        
        for chart in charts_list:
            chart["_id"] = str(chart["_id"])
        
        return charts_list 
        
    except Exception as e:
        return {"error": str(e)} 
    
def clear_chart_history(asset_id):
    try:
        result = chart_history_collection.delete_many({"asset_id": asset_id})
        print(f"Deleted {result.deleted_count} chart history entries for asset_id: {asset_id}")
    except PyMongoError as e:
        print(f"MongoDB error: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise

