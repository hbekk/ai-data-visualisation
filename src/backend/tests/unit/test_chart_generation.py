import pytest
import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# IMPORTS
from models.chart_generation import manual_chart_builder 

def test_manual_chart_builder_basic():
    data_input = [
        ("2025-04-22 14:00:00", 5.5),
        ("2025-04-22 15:00:00", 6.1),
    ]
    
    result = manual_chart_builder(data_input, "test", "PH Sensor")
    
    assert result["chartType"] == "line"
    assert result["chartData"]["datasets"][0]["label"] == "PH Sensor"
    assert result["chartData"]["datasets"][0]["data"] == [5.5, 6.1]
    assert result["chartData"]["labels"] == [
        "2025-04-22T14:00:00",
        "2025-04-22T15:00:00"
    ]
    assert result["chartOptions"]["scales"]["x"]["type"] == "time"

def test_manual_chart_builder_zeros_filtered():
    data_input = [
        ("2025-04-22 14:00:00", 0),
        ("2025-04-22 15:00:00", 4.2),
    ]
    
    result = manual_chart_builder(data_input, "test", "Turbidity Sensor")
    
    assert result["chartData"]["labels"] == ["2025-04-22T15:00:00"]
    assert result["chartData"]["datasets"][0]["data"] == [4.2]

def test_manual_chart_builder_empty_input():
    result = manual_chart_builder([], "test", "Empty Test")
    
    assert result["chartData"]["labels"] == []
    assert result["chartData"]["datasets"][0]["data"] == []
    assert result["chartData"]["datasets"][0]["label"] == "Empty Test"
