from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv("../../.env.local")
my_api_key = os.getenv("GEMINI_API_KEY")

#MANUAL
def manual_chart_builder(nums, query, sensor_name):
    labels = []
    data = []

    for items in nums:
        isotime, value = items
        if value != 0: 
            labels.append(str(isotime))  
            data.append(value) 

    iso_labels = [datetime.strptime(label, "%Y-%m-%d %H:%M:%S").isoformat() for label in labels]

    chart_label = sensor_name.strip()

    chart_config = {
        "type": "line",
        "data": {
            "labels": iso_labels,
            "datasets": [{
                "label": chart_label,
                "data": data,
                "borderColor": "rgb(0, 243, 255)",
                "backgroundColor": "rgb(0, 243, 255)"
            }]
        },
        "options": {
            "plugins": {
                "title": {
                "display": True,
                "text": query,
            "font": {
                "size": 15,         
                "weight": "bold"  
            },
                "color": "white"
       }
            },
            "scales": {  
                "x": {
                    "type": "time",
                    "time": {
                        "unit": "hour",
                        "displayFormats": {"hour": "HH"},
                    },
                },
                "y": {
                    "grid": {"color": "rgba(255, 255, 255, 0.2)"},
                }
            }
        }
    }

    return {
    "chartData": chart_config["data"],
    "chartOptions": chart_config["options"],
    "chartType": chart_config["type"],
    "llmTitle": query,
    }
