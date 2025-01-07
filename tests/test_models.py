"""Test model extraction functionality."""
import pytest
from unittest.mock import Mock
from src.app.main import extract_model_names

def test_extract_model_names_empty():
    """Test extracting model names from empty response."""
    models_info = Mock()
    models_info.models = []
    result = extract_model_names(models_info)
    assert result == tuple()

def test_extract_model_names_success():
    """Test successful model name extraction."""
    # Create mock Model objects
    mock_model1 = Mock()
    mock_model1.model = "model1:latest"
    mock_model2 = Mock()
    mock_model2.model = "model2:latest"
    
    # Create mock response
    models_info = Mock()
    models_info.models = [mock_model1, mock_model2]
    
    result = extract_model_names(models_info)
    assert result == ("model1:latest", "model2:latest")

def test_extract_model_names_invalid_format():
    """Test handling invalid response format."""
    models_info = {"invalid": "format"}
    result = extract_model_names(models_info)
    assert result == tuple()

def test_extract_model_names_exception():
    """Test handling exceptions during extraction."""
    models_info = Mock()
    # Accessing .models will raise AttributeError
    del models_info.models
    result = extract_model_names(models_info)
    assert result == tuple() 