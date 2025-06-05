import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Any
from fastapi import HTTPException
import json
from fastapi.responses import JSONResponse

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request



## FUNCTION IMPORTS

##Pipeline Processors
from models.chart_generation import manual_chart_builder #Pipeline 1
from models.embeddings import process_user_query #Pipeline 2
from models.llm_pipeline import process_llm_pipeline #Pipeline 3

from models.chart_archiving import addArchivedChart
from models.chart_archiving import get_chart_data
from models.chart_archiving import remove_saved_data, get_chart_history, addChartHistory, clear_chart_history

from models.prompt_suggestions import get_suggested_prompts

from utils.manual_query_processor import process_manual_query

from utils.fetch_assets import fetch_assets_from_db

from utils.sensor_parser import extract_sensor

from utils.pipelines import try_manual_pipeline, try_rag_pipeline

load_dotenv("../../.env.local")

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    asset_id: str

class ChartData(BaseModel):
    chartData: Any
    chartOptions: Any
    chartType: str
    date: int
    title: str
    asset_id: str
    previousQueries: list

class removeData(BaseModel):
    timestamp: int

class asset_req(BaseModel):
    asset_id: str  

class PromptRequest(BaseModel):
    query: str 
    asset_id: str
    previousQuery: list[str]


@app.get("/")
def read_root():    
    return {"Hello": "World test"}

@app.post("/query")
@limiter.limit("10/minute")
async def process_query(query_request: PromptRequest, request: Request):
    query = query_request.query
    asset_id = query_request.asset_id
    prev = query_request.previousQuery

    print(f"Received query: '{query}' for asset_id: {asset_id}")

    if query.lower().startswith("reply"):
        return process_llm_pipeline(query, asset_id, prev, isReply=True)

    expected_sensors = extract_sensor(query)

    # 1. Pipeline 1: Manual
    manual_result = try_manual_pipeline(query, asset_id, expected_sensors)
    if manual_result:
        return manual_result

    # 2. Pipeline 2: RAG
    rag_result = try_rag_pipeline(query, asset_id)
    if rag_result:
        return rag_result

    # Pipeline 3: LLM
    print("Routing to LLM.")
    return process_llm_pipeline(query, asset_id, previous_prompts=None, isReply=False)



@app.post("/save_chart")
@limiter.limit("20/minute")
async def process_saving_chart(data: ChartData, request: Request):
    try:
        # Convert the ChartData to a dictionary and then to a JSON string
        chart_dict = data.dict()  # Convert the Pydantic model to a dictionary
        chart_json = json.dumps(chart_dict)  # Convert the dictionary to a JSON string

        addArchivedChart(chart_json)

        return {"message": "Chart saved successfully!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
@app.post("/save_chart_history")
@limiter.limit("20/minute")
async def process_saving_chart_history(data: ChartData, request: Request):
    try:
        # Convert the ChartData to a dictionary and then to a JSON string
        chart_dict = data.dict()  # Convert the Pydantic model to a dictionary

        addChartHistory(chart_dict)

        return {"message": "Chart history saved successfully!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
@app.post("/get_chart_history")
@limiter.limit("20/minute")
async def process_getting_chart_history(data: asset_req, request: Request):
   history_data = get_chart_history(data.asset_id)
   return JSONResponse(content={"data": history_data}) 

@app.post("/api/clear-chart-history/")
@limiter.limit("20/minute")
async def delete_chart_history(data: asset_req, request: Request):
    try:
        clear_chart_history(data.asset_id)
        return JSONResponse(content={"message": "Chart history cleared"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    

@app.post("/get_chart_data")
@limiter.limit("20/minute")
async def process_getting_saved_charts(data: asset_req, request: Request):
   list = get_chart_data(data.asset_id)
   return JSONResponse(content={"data": list})  

@app.post("/remove_saved_chart")
@limiter.limit("20/minute")
async def remove_saved_chart(data: removeData, request: Request):
    post_id = data.timestamp
    remove_saved_data(post_id)
    return JSONResponse(content={"data": post_id})   

@app.get("/assets")
@limiter.limit("3/minute")
async def get_assets(request: Request):
    assets = fetch_assets_from_db()
    print(assets)
    return JSONResponse(content={"data": assets})

@app.post("/api/prompt-suggestions/")
@limiter.limit("20/minute")
async def suggest_prompts(request: Request):
    data = await request.json()
    asset_id = data.get("asset_id")
    suggestions = get_suggested_prompts(asset_id)
    return JSONResponse(content={"suggestions": suggestions})





