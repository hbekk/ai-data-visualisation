from utils.mongo_executor import execute_queries  
from utils.chart_utils import generate_chart_from_query_results, fill_pie_chart_data
from models.mongo_query_generation import generate_mongo_query_from_prompt

def process_llm_pipeline(user_query, asset_id, previous_prompts, isReply):
    print(f"Pipeline 3 is running for: {user_query}")

    if not previous_prompts:
        previous_prompts = []
    if isinstance(previous_prompts, str):
        previous_prompts = [previous_prompts]

    prompt_history = " then ".join(previous_prompts)
    combined_prompt = f"{prompt_history} // {user_query}" if prompt_history else user_query

    mongo_query_result = generate_mongo_query_from_prompt(combined_prompt, prompt_history)

    if not mongo_query_result:
        return {"error": "Failed to generate MongoDB query."}
    if isinstance(mongo_query_result, dict) and mongo_query_result.get("success") is False:
        return mongo_query_result

    raw_query = mongo_query_result["query"]
    chart_intent = mongo_query_result["intent"]

    query_results = execute_queries([raw_query], asset_id)

    if isinstance(query_results, dict) and (query_results.get("error") or query_results.get("success") is False):
        return query_results

    return generate_chart_from_query_results(
        user_query=user_query,
        query_results=query_results,
        chartType=None,
        previousPrompt=prompt_history  
    )

    

