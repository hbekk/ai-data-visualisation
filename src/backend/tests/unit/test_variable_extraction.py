import pytest
import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

## IMPORTS 
from models.embeddings import extract_variables
from utils.sensor_parser import extract_sensor
from utils.date_parser import extract_all_dates

## TESTS VARIABLE EXTRACTION

@patch("utils.sensor_parser.get_sensor_types")
def test_variable_extraction_single_date(mock_extract_sensor):
    mock_extract_sensor.return_value = ["ph in", "turbidity in", "ph out"]

    matched_sensors, mongo_dates, hour_start, hour_end, error_message = extract_variables("ph in values on 28 september 2022 at 4pm")

    for i in range(len(matched_sensors)):
        matched_sensors[i] = matched_sensors[i].lower()
        assert matched_sensors[i] == "ph in"

    for i in range(len(mongo_dates)):
        assert str(mongo_dates[i]) == "2022-09-28 00:00:00+00:00"
    
    assert hour_start == 16
    assert hour_end == 17
 

@patch("utils.sensor_parser.get_sensor_types")
def test_variable_extraction_multiple_sensors(mock_extract_sensor):
    mock_extract_sensor.return_value = ["ph in", "turbidity in", "ph out"]

    matched_sensors, mongo_dates, hour_start, hour_end, error_message = extract_variables("ph in values, turbidity in, and ph out in values on 30 september 2022 at 4pm")

    expected_sensors = ["ph in", "turbidity in", "ph out"]
    
    matched_sensors = [sensor.lower() for sensor in matched_sensors]
    assert sorted(matched_sensors) == sorted(expected_sensors)

    for i in range(len(mongo_dates)):
        assert str(mongo_dates[i]) == "2022-09-30 00:00:00+00:00"
    
    assert hour_start == 16
    assert hour_end == 17

@patch("utils.sensor_parser.get_sensor_types")
def test_sensor_extraction_no_match(mock_extract_sensor):
    mock_extract_sensor.return_value = ["ph in", "turbidity in", "ph out"]

    results = extract_sensor("temperature values, rotor speed, and co2 levels in values on 30 september 2022 at 4pm")

    assert results == {"error": "Unknown sensor type."}

#Pipeline 2 Date Extraction
def test_date_extraction_no_dates():
    valid_dates, mongo_dates, hour_start, hour_end, error_message = extract_all_dates("ph in values 2022")
    assert error_message == "Could not extract valid dates."

def test_date_extraction_short_dates():
    valid_dates, mongo_dates, hour_start, hour_end, error_message = extract_all_dates("ph in values 28 sep 2022")
    assert valid_dates[0] == "2022-09-28"
    
