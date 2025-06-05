from sentence_transformers import SentenceTransformer, util
from bson.binary import Binary, BinaryVectorDtype
from datetime import datetime, timezone
import re
from .database import vector_collection  
from .database import collection as Telemetry
from utils.chart_utils import generate_chart_from_query_results
from models.llm_chart import generate_text_from_query_results
from utils.date_parser import extract_all_dates
from utils.mongo_executor import execute_queries
from utils.sensor_parser import extract_sensor
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2", trust_remote_code=True)

######### EMBEDDINGS

def get_embedding(data, precision="float32"):
    embeddings = model.encode(data)
    if precision == "float32":
        embeddings = embeddings.astype(np.float32)
    return embeddings

def generate_vector(vector):
    return vector.tolist()

def create_docs_with_bson_vector_embeddings(bson_float32, data):
    docs = []

    for (embedding, query) in zip(bson_float32, data): 
        doc = {
            "natural_query": query[0],  
            "mongo_query": query[1],    
            "BSON-Float32-Embedding": embedding, 
            "isText": query[3],
            "chartType": query[4]
        }
        docs.append(doc)
    return docs

######### SEARCHING QUERY TEMPLATE

def vector_search(user_query):
    query_embedding = get_embedding(user_query, precision="float32")
    bson_query_embedding = generate_vector(query_embedding)

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_search",
                "queryVector": bson_query_embedding,
                "path": "BSON-Float32-Embedding",
                "numCandidates": 3,
                "exact": False,
                "limit": 1
            }
        },{
            "$addFields": {"score": {"$meta": "vectorSearchScore"}}
        },
        {
            "$match": {"score": {"$gte": 0.4}}
        },
        {
            "$project": {
                "_id": 0,
                "natural_query": 1,
                "mongo_query": 1,
                "isText": 1,
                "chartType": 1,
                "score": { "$meta": "vectorSearchScore" }
            }
        }
    ]

    results = list(vector_collection.aggregate(pipeline))

    if results:
        print(f"Matched Query: {results[0]['natural_query']}")
        return results[0]["mongo_query"], results[0]['natural_query'], results[0]['isText'], results[0]['chartType']

    print("No match.")
    return None, None

######### EXTRACT VARIABLES 

def extract_variables(user_query):

    extracted_dates, mongo_dates, hour_start, hour_end, error_message = extract_all_dates(user_query)

    matched_sensors = extract_sensor(user_query)
    
    if error_message:
        print(error_message)
        return None, None, error_message
    
    if isinstance(matched_sensors, dict) and "error" in matched_sensors:
        print(matched_sensors["error"])
        return None, None, matched_sensors["error"]

    if isinstance(matched_sensors, list):
        print(f"Matched Sensors: {matched_sensors}")
    else:
        matched_sensors = [matched_sensors]
        print(f"Matched Sensor: {matched_sensors}")

    print(f"\n Dates: {mongo_dates}")
    print(f"\n TOD: {hour_start, hour_end} \n")


    return matched_sensors, mongo_dates, hour_start, hour_end, None



######### FILL MONGO QUERY TEMPLATE

def fill_query(template_query, object_names, dates, time_hour_begin, time_hour_end):
    if not template_query:
        print("No template query found")
        return None

    if not isinstance(template_query, dict):
        print(f"Template query is not a dictionary! It is: {type(template_query)}")
        return None
    
    filled_queries = []

    for date in dates:
        query_filled = template_query.copy()

        try:
            if time_hour_begin is None and time_hour_end is None:
                query_filled["timestamp"] = {
                "$gte": date.replace(hour=0, minute=0, second=0, tzinfo=timezone.utc),
                "$lt": date.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
                }
                
            else:
                hour_begin = int(time_hour_begin)
                hour_end = int(time_hour_end)

                query_filled["timestamp"] = {
                "$gte": date.replace(hour=hour_begin, minute=0, second=0, tzinfo=timezone.utc),
                "$lt": date.replace(hour=hour_end, minute=59, second=59, tzinfo=timezone.utc)
                }

            if isinstance(object_names, list) and len(object_names) > 1:
                query_filled["metadata.name"] = {"$in": object_names}
            else:
                query_filled["metadata.name"] = object_names[0]  

            filled_queries.append(query_filled)
        except KeyError:
            print(f"Template query is missing fields for date {date}!")
            return None

    return filled_queries  


######### QUERY EXECUTION

def process_pipeline_2_queries(filled_queries):
    return execute_queries(filled_queries)

######### PIPELINE 2 RUN

def process_user_query(user_query, asset_id):
    query_template, matched_query, isText, chartType = vector_search(user_query)

    print("Chart Type:", chartType)

    if not query_template:
        return {"error": "No matching query template found."}
    
    object_name, dates, hour_start, hour_end, error = extract_variables(user_query)

    if error or object_name is None:
        object_name = "Unknown"

    final_queries = fill_query(query_template, object_name, dates, hour_start, hour_end)

    if not final_queries:
        return {"error": "Query filling failed."}

    raw_results = execute_queries(final_queries, asset_id)

    if isText is True:
        print("Text answer needed")
        explanation = generate_text_from_query_results(user_query, raw_results, sensor_name=object_name)

        if isinstance(explanation, dict) and "message" in explanation:
            return {
            "success": True,
            "type": "text",
            "content": explanation["message"]
        }

        if isinstance(explanation, str):
            return {
            "success": True,
            "type": "text",
            "content": explanation
        }

        return {
        "success": False,
        "message": "Invalid format returned by generate_text_from_query_results"
    }

    else:
        chart = generate_chart_from_query_results(user_query, raw_results, chartType, previousPrompt=None)
        if chart:
            return generate_chart_from_query_results(user_query, raw_results, chartType, previousPrompt=None)
        else:
            return{
                "success": False,
                "message": "Invalid chart generated"
            }

   

   