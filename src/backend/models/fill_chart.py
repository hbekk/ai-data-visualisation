import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
from collections import defaultdict 
from models.llm_chart import generate_llm_chart_config

def generate_time_grid(start_time, end_time, interval_minutes=5):
    if not isinstance(interval_minutes, int):
        print(f"ERROR: interval_minutes is not an integer: {interval_minutes}")
        return []

    times = []
    current_time = start_time
    while current_time <= end_time:
        times.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=interval_minutes)
    return times

#Config chart to fix any LLM chart code
def generate_chart_config(chart_config, grouped_data, all_timestamps, interval_minutes):
    
    min_time = min(dt.time() for dt in all_timestamps)  
    max_time = max(dt.time() for dt in all_timestamps)  

    reference_date = datetime(2000, 1, 1)  
    start_time = datetime.combine(reference_date, min_time)
    end_time = datetime.combine(reference_date, max_time)

    shared_time_labels = generate_time_grid(start_time, end_time, interval_minutes)
    
    chart_config["data"]["datasets"] = []

    colors = [
        "rgb(0, 243, 255)", "rgb(255, 99, 132)", "rgb(255, 206, 86)", "rgb(153, 102, 255)","rgb(255, 159, 64)", "rgb(54, 162, 235)", "rgb(201, 203, 207)"  
    ]

    color_index = 0  

    for sensor_name, date_data in grouped_data.items():
        for date in sorted(date_data.keys()):
            data = date_data[date]
            dataset_values = [
                {"x": time, "y": data.get(time, None)}
                for time in shared_time_labels
            ]

            color = colors[color_index % len(colors)]
            color_index += 1

            dataset = {
                "label": f"{sensor_name} - {date}",
                "data": dataset_values,
                "borderColor": color,
                "backgroundColor": color,
                "borderWidth": 2,
                "fill": False,
                "pointRadius": 3,
                "tension": 0,
                "spanGaps": True,
            }
            chart_config["data"]["datasets"].append(dataset)

    chart_config["data"]["labels"] = shared_time_labels

    chart_config.setdefault("options", {})
    chart_config["options"].setdefault("scales", {})

    chart_config["options"]["scales"]["x"] = {
    "type": "category",
    "labels": shared_time_labels,
    "ticks": {
        "autoSkip": True,
        "maxTicksLimit": 10,
        "minRotation": 45
    }
}

    chart_config["options"]["scales"].setdefault("y", {})
    if "grid" not in chart_config["options"]["scales"]["y"]:
            chart_config["options"]["scales"]["y"]["grid"] = {
        "color": "rgba(255, 255, 255, 0.2)"
    }
    
    return json.dumps(chart_config)


def fill_llm_chart_data(chart_config, sensor_data, sensor_label=None, interval_minutes=5):
    if not isinstance(interval_minutes, int):
        interval_minutes = 5

    if not chart_config or not isinstance(chart_config, dict):
        return None

    try:
        grouped_data = defaultdict(lambda: defaultdict(dict))  
        all_timestamps = []

        print(f"DEBUG: Incoming Sensor Data Length: {len(sensor_data)}")

        for entry in sensor_data:
            timestamp = entry.get("timestamp")
            value = entry.get("value")

            if isinstance(sensor_label, list):
                sensor_name = entry["metadata"]["name"] if "metadata" in entry and "name" in entry["metadata"] else "Unknown Sensor"
            else:
                sensor_name = sensor_label  

            if timestamp is None or value is None:
                continue  

            dt = timestamp if isinstance(timestamp, datetime) else datetime.fromisoformat(str(timestamp))
            all_timestamps.append(dt)

            time_str = dt.strftime("%H:%M")  
            date_str = dt.date().isoformat()  

            grouped_data[sensor_name][date_str][time_str] = value  

        if not all_timestamps:
            print("ERROR: No valid timestamps found.")
            return None

        is_daily_grouped = all(dt.hour == 0 and dt.minute == 0 for dt in all_timestamps)

        if is_daily_grouped:
            chart_config["data"]["datasets"] = []
            chart_config["data"]["labels"] = []

            colors = [
                "rgb(0, 243, 255)", "rgb(255, 99, 132)", "rgb(255, 206, 86)",
                "rgb(153, 102, 255)", "rgb(255, 159, 64)", "rgb(54, 162, 235)", "rgb(201, 203, 207)"
            ]
            color_index = 0


            for sensor_name, date_data in grouped_data.items():
                daily_points = sorted([
                    {"x": date, "y": list(values.values())[0]}
                    for date, values in date_data.items()
                ], key=lambda x: x["x"])

                color = colors[color_index % len(colors)]
                color_index += 1

                dataset = {
                    "label": sensor_name,
                    "data": daily_points,
                    "borderColor": color,
                    "backgroundColor": color,
                    "fill": False,
                    "tension": 0,
                    "pointRadius": 4,
                    "spanGaps": True
                }


                chart_config["data"]["datasets"].append(dataset)
                chart_config["data"]["labels"] = [pt["x"] for pt in daily_points]

            chart_config.setdefault("options", {}).setdefault("scales", {})
            chart_config["options"]["scales"]["x"] = {
                "type": "category",
                "labels": chart_config["data"]["labels"],
                "ticks": {
                    "autoSkip": False,
                    "minRotation": 45
                }
            }

            return json.dumps(chart_config)

        return generate_chart_config(chart_config, grouped_data, all_timestamps, interval_minutes)

    except Exception as e:
        print("ERROR while filling chart data:", str(e))
        return None




def fill_pie_chart_data(sensor_data, user_query="Distribution of sensor values", query_results=None, previousPrompt=None):
    if not sensor_data or not isinstance(sensor_data, list):
        return None

    labels = []
    data_values = []

    for entry in sensor_data:
        _id = entry.get("_id", "Unknown")
        count = entry.get("count", 0)

        if isinstance(_id, dict):
            label = ", ".join([f"{k}: {v}" for k, v in _id.items()])
        elif _id is None:
            label = "Unknown"
        else:
            label = str(_id)

        labels.append(label)
        data_values.append(count)

    colors = [
        "rgb(255, 99, 132)", "rgb(54, 162, 235)", "rgb(255, 206, 86)",
        "rgb(75, 192, 192)", "rgb(153, 102, 255)", "rgb(255, 159, 64)",
        "rgb(0, 243, 255)", "rgb(128, 128, 128)", "rgb(255, 105, 180)",
        "rgb(60, 179, 113)", "rgb(255, 140, 0)", "rgb(100, 149, 237)"
    ]
    background_colors = [colors[i % len(colors)] for i in range(len(labels))]

    try:
        sensor_names = list(set(
            entry.get("metadata", {}).get("name")
            for entry in (query_results or [])
            if isinstance(entry, dict) and "metadata" in entry and "name" in entry["metadata"]
        ))
        sensor_names = [name for name in sensor_names if name]
    except Exception:
        sensor_names = []

    sensor_context = ", ".join(sensor_names) if sensor_names else "Sensor"

    class Summary:
        def __init__(self, length, avg):
            self.length = length
            self.avg = avg
            self.median = 0
            self.std_dev = 0
            self.min = 0
            self.max = 0

    summary_stats = Summary(
        length=len(data_values),
        avg=sum(data_values) / len(data_values) if data_values else 0
    )

    llm_result = generate_llm_chart_config(
        sensor_name=sensor_context,
        num_data_points=len(data_values),
        query=user_query,
        summary_stats=summary_stats,
        providedChartType="pie",
        previous_Prompt=previousPrompt
    )

    chart_config = llm_result.get("config", {})

    if "data" not in chart_config:
        chart_config["data"] = {}

    if "datasets" not in chart_config["data"] or not chart_config["data"]["datasets"]:
        chart_config["data"]["datasets"] = [{}]

    chart_config["type"] = "pie"
    chart_config["data"]["labels"] = labels
    chart_config["data"]["datasets"][0]["label"] = user_query
    chart_config["data"]["datasets"][0]["data"] = data_values
    chart_config["data"]["datasets"][0]["backgroundColor"] = background_colors
    chart_config["data"]["datasets"][0]["borderColor"] = background_colors

    return json.dumps(chart_config, indent=2)

