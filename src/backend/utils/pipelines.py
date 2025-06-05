import json
from utils.manual_query_processor import process_manual_query
from models.chart_generation import manual_chart_builder
from models.embeddings import process_user_query

def try_manual_pipeline(query: str, asset_id: str, expected_sensors: list[str]):
    try:
        if isinstance(expected_sensors, dict) and "error" in expected_sensors:
            print(f"[Manual] Sensor parse failed: {expected_sensors['error']}")
            return None

        if any(word in query.lower() for word in ["lowest", "highest", "average", "mean", "median", "maximum", "minimum", "difference"]):
            print(f"[Manual] Skipping due to statistical intent in query: '{query}'")
            return None
        
        if any(word in query.lower() for word in ["scatter", "bar", "line", "pie"]):
            print(f"[Manual] Skipping due to specified chart type: '{query}'")
            return None

        if len(expected_sensors) > 1:
            print(f"[Manual] Skipping — multiple sensors ({expected_sensors}) detected (manual only supports 1)")
            return None

        response, sensor_name = process_manual_query(query, asset_id)

        if isinstance(response, dict) and "error" in response:
            print(f"[Manual] Error: {response['error']}")
            return None

        if isinstance(response, list):
            print("[Manual] Success")
            return manual_chart_builder(response, query, sensor_name)

    except Exception as e:
        print(f"[Manual] Exception: {str(e)}")
        return None


def try_rag_pipeline(query: str, asset_id: str):
    try:
        rag_result = process_user_query(query, asset_id)

        if not isinstance(rag_result, dict):
            print("[RAG] Unexpected response format")
            return None

       

        if rag_result.get("type") == "text":
            print("[RAG] Text explanation returned")
            return {
                    "success": True,
                    "message": rag_result.get("content", "No message provided."),
                    "type": "text"
                }

        if rag_result:
            print("[RAG] Chart returned")
            return rag_result
            
        if rag_result.get("success") is False:
            print(f"[RAG] Failed: {rag_result.get('message', 'No message provided')}")

        print(f"[RAG] Final response: {json.dumps(rag_result, indent=2)}")
        print("[RAG] No usable output")
        return None

    except Exception as e:
        print(f"[RAG] Exception: {str(e)}")
        return None

