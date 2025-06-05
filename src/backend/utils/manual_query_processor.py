from utils.date_parser import extract_date_range
from utils.sensor_parser import extract_sensor
from models.general_queries import fetch_sensor_values
import json
from collections import defaultdict
from datetime import datetime

def process_manual_query(query_text: str, asset_id:str):

    start_date, end_date, error_message = extract_date_range(query_text)

    if error_message:
        return {"error": "Invalid date format."}, "pH"

    sensor_name = extract_sensor(query_text)

    if isinstance(sensor_name, dict) and "error" in sensor_name:
        return {"error": sensor_name["error"]}, None

    return fetch_sensor_values(start_date, end_date, sensor_name[0], asset_id, limit=50), sensor_name[0]



