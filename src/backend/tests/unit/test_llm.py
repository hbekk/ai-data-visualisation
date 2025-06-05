import pytest
import sys
import os
from unittest.mock import patch, MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

## IMPORTS
from models.llm_chart import generate_text_from_query_results

## LLM 

def test_llm_text_error_when_db_query_results_empty():
    result = generate_text_from_query_results("Test query", [], "ph in")
    assert "error" in result
    assert result["error"] == "No data retrieved from MongoDB."

