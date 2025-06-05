import json
from datetime import datetime
from pymongo import ASCENDING
import google.generativeai as genai
import os
from .database import collection as Telemetry  
from dotenv import load_dotenv
from utils.sensor_parser import get_sensor_types
from utils.date_parser import today_str

load_dotenv("../../.env.local")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash")


def generate_mongo_query_from_prompt(prompt, previousPrompt):
    reference_query_sensors = {
        "metadata": {"name": {"$in": ["pH in", "pH out"]}},
        "timestamp": {
            "$gte": "2022-09-27T00:00:00Z",
            "$lt": "2022-09-27T23:59:59Z"
        },
        "sort": {"timestamp": 1}
    }

    reference_query_distribution = [
        {"$match": {
            "timestamp": {
                "$gte": "2022-09-27T00:00:00Z",
                "$lt": "2022-09-27T23:59:59Z"
            }
        }},
        {"$group": {"_id": "$value", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]

    known_sensors = get_sensor_types()
    sensor_list_string = "\n- " + "\n- ".join(sorted(known_sensors))

    system_instruction = (f"""
You are an AI that generates MongoDB queries based on user requests. 
Your response **must be a JSON object** or a list of aggregation stages depending on the user's intent.
Today's date is {today_str}.

### Valid Sensor Names:
{sensor_list_string}

### 1. Standard Sensor Queries (Line/Bar Charts):
{json.dumps(reference_query_sensors, indent=2)}

### 2. Pie Chart (Distribution Queries):
{json.dumps(reference_query_distribution, indent=2)}

### 3. Grouped by Day (Daily Averages):
If the user asks for *daily averages*, *grouped by day*, *average per day*, *summarised by date*, etc.,
return a MongoDB aggregation pipeline that:
- Filters data by time range and sensor(s)
- Groups by `$dateToString: {{ format: '%Y-%m-%d', date: '$timestamp' }}` and sensor name
- Calculates the average using `$avg`
- Sorts results by date

**Example:**
{json.dumps([
    {"$match": {
        "metadata.name": "pH in",
        "timestamp": {
            "$gte": "2022-09-01T00:00:00Z",
            "$lt": "2022-10-01T00:00:00Z"
        }
    }},
    {"$group": {
        "_id": {
            "date": { "$dateToString": { "format": "%Y-%m-%d", "date": "$timestamp" }},
            "sensor": "$metadata.name"
        },
        "averageValue": { "$avg": "$value" }
    }},
    {"$sort": { "_id.date": 1 }}
], indent=2)}

### Rules for Query Generation
- This was the previous prompts "{previousPrompt}". If populated it is the previous prompts in the conversation starting with the oldest.
if it is not an empty string, then you should treat your reply as the next in that conversation. Interpert accordingly. If not, just use the newest prompt.
- You should always query using the provided user query, but use previous prompts as context for adjustment (such as dates).
- Use `$in` if multiple sensors are requested.
- If the user prompt includes words like **distribution**, **proportion**, **percent**, or **pie chart**, return an **aggregation pipeline** (list).
- If the user prompt includes phrases like **grouped by day**, **daily average**, **per day**, **summarised by date**, return an **aggregation pipeline** that groups by date and sensor name.
- For everything else, return a **standard MongoDB query** (JSON object).
- NEVER return markdown, explanations, or text. Only valid MongoDB JSON.

### Additional Rule for Dates:
If the user request contains natural language time expressions (e.g. yesterday, last week, past 3 days, from Monday to Friday, this weekend):
- You MUST convert all such expressions into **explicit ISO 8601 date strings** in the final query.
- Use YYYY-MM-DDT00:00:00Z for `$gte`, and YYYY-MM-DDT23:59:59Z for `$lt`.
- Use today's date as reference: {today_str}.
- DO NOT leave any natural expressions like yesterday or this week in the output.
"""
)
    print(f"Sending prompt to LLM for query generation: {prompt}")

    try:
        response = model.generate_content(f"{system_instruction}\nUser Query: {prompt}")
        raw_response = response.text.strip()

        clean_response = raw_response.strip("```json").strip("```").strip()
        mongo_query = json.loads(clean_response)

        def query_has_known_sensor(q, known_sensors):
            if isinstance(q, dict) and "metadata" in q and isinstance(q["metadata"], dict):
                name = q["metadata"].get("name")
                if isinstance(name, str):
                    return name in known_sensors
                elif isinstance(name, dict) and "$in" in name:
                    return any(n in known_sensors for n in name["$in"])
            if isinstance(q, dict) and "metadata.name" in q:
                name = q["metadata.name"]
                if isinstance(name, str):
                    return name in known_sensors
                elif isinstance(name, dict) and "$in" in name:
                    return any(n in known_sensors for n in name["$in"])
            return True  


        if not query_has_known_sensor(mongo_query, known_sensors):
            return {
            "success": False,
            "message": "Sorry, I did not recognise any valid sensors in your request."
        }


        def query_has_timeframe(q):
            if isinstance(q, dict) and "timestamp" in q:
                return True
            if isinstance(q, list):
                for stage in q:
                    if "$match" in stage and "timestamp" in stage["$match"]:
                        return True
            return False

        if not query_has_timeframe(mongo_query):
            return {
        "success": False,
        "message": "Please include a timeframe."
    }
        


        if isinstance(mongo_query, list):
            for stage in mongo_query:
                if "$match" in stage and "timestamp" in stage["$match"]:
                    ts = stage["$match"]["timestamp"]
                    if "$gte" in ts:
                        ts["$gte"] = datetime.fromisoformat(ts["$gte"].replace("Z", "+00:00"))
                    if "$lt" in ts:
                        ts["$lt"] = datetime.fromisoformat(ts["$lt"].replace("Z", "+00:00"))

        elif isinstance(mongo_query, dict) and "timestamp" in mongo_query:
            ts = mongo_query["timestamp"]
            if "$gte" in ts:
                ts["$gte"] = datetime.fromisoformat(ts["$gte"].replace("Z", "+00:00"))
            if "$lt" in ts:
                ts["$lt"] = datetime.fromisoformat(ts["$lt"].replace("Z", "+00:00"))

        print(f"Final MongoDB Query: {json.dumps(mongo_query, indent=2, default=str)}")
        query_type = "pie" if isinstance(mongo_query, list) else "standard"

        return {
            "query": mongo_query,
            "intent": query_type
        }
    

    except json.JSONDecodeError as e:
        print("LLM JSON Error:", str(e))
        return None
    except Exception as e:
        print("LLM Error:", str(e))
        return None
