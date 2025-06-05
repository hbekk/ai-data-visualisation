import json
from utils.data_calculations import calc_pipeline
from models.llm_chart import generate_llm_chart_config
from models.fill_chart import fill_pie_chart_data, fill_llm_chart_data


def generate_chart_from_query_results(user_query, query_results, chartType, previousPrompt):
    if not query_results or not isinstance(query_results, list):
        return {"error": "No data retrieved from MongoDB."}
    
    is_aggregated = "_id" in query_results[0] and "count" in query_results[0]
    if is_aggregated:
        filled_config = fill_pie_chart_data(query_results, user_query, query_results)
        parsed_config = json.loads(filled_config)
    
        return {
            "chartData": parsed_config["data"],
            "chartOptions": parsed_config.get("options", {}),
            "chartType": parsed_config["type"],
            "llmTitle": parsed_config.get("options", {}).get("plugins", {}).get("title", {}).get("text", "")
    }



    sensor_names = list(set(
        entry["metadata"]["name"]
        for entry in query_results
        if "metadata" in entry and "name" in entry["metadata"]
    ))

    sensor_values = [
        entry["value"]
        for entry in query_results
        if "value" in entry and isinstance(entry["value"], (int, float))
    ]

    data_summary = calc_pipeline(sensor_values)
    print(f"Stats: Std Dev: {data_summary.std_dev}, Avg: {data_summary.avg}, Median: {data_summary.median}, Count: {data_summary.length}")

    sensor_context = (
    ", ".join(sensor_names)
    if sensor_names else "Unknown Sensor"    
    )

    llm_result = generate_llm_chart_config(
        sensor_name=sensor_context,
        num_data_points=data_summary.length,
        query=user_query,
        summary_stats=data_summary,
        providedChartType=chartType,
        previous_Prompt=previousPrompt
    )

    if not llm_result:
        return {"error": "Failed to generate chart config from LLM."}

    chart_type = llm_result["chart_type"]
    chart_config = llm_result["config"]

    if chart_type == "pie":
        filled_config = fill_pie_chart_data(query_results, user_query, query_results)
    else:
        filled_config = fill_llm_chart_data(chart_config, query_results, sensor_label=sensor_names)

    parsed_config = json.loads(filled_config)

    return {
    "chartData": parsed_config["data"],
    "chartOptions": parsed_config["options"],
    "chartType": parsed_config["type"],
    "llmTitle": parsed_config["options"]["plugins"]["title"]["text"]
}

