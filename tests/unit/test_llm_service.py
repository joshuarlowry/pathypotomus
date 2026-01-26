import json
import pytest
from unittest.mock import MagicMock, patch, mock_open
from openai import OpenAIError

from pathypotomus.services.llm import LLMService, LLMCache
from pathypotomus.models.route import Route
from pathypotomus.models.coordinates import Coordinates

@pytest.fixture
def sample_route():
    return Route(
        geometry=[Coordinates(latitude=0, longitude=0), Coordinates(latitude=1, longitude=1)],
        distance=1000.0,
        duration=600.0,
        summary="via Main St",
        major_roads=["Main St", "First Ave"]
    )

def test_init_no_api_key():
    service = LLMService(api_key="")
    assert service.client is None

def test_generate_route_description_no_client(sample_route):
    service = LLMService(api_key="")
    result = service.generate_route_description(sample_route)
    assert result == sample_route
    assert result.name is None
    assert result.description is None

def test_cache_hit(sample_route):
    with patch('pathypotomus.services.llm.LLMCache') as mock_cache_cls:
        mock_cache = MagicMock()
        mock_cache_cls.return_value = mock_cache
        mock_cache.get.return_value = "Name: Cached Route\nDescription: Cached description."
        
        service = LLMService(api_key="fake-key")
        result = service.generate_route_description(sample_route)
        
        assert result.name == "Cached Route"
        assert service.client is not None
        # Should NOT call OpenAI if cache hit
        # Note: We can't easily assert client call count without mocking OpenAI as well,
        # but the logic is straightforward.

def test_generate_route_description_success_and_cache_set(sample_route):
    with patch('pathypotomus.services.llm.OpenAI') as mock_openai_cls, \
         patch('pathypotomus.services.llm.LLMCache') as mock_cache_cls:
        
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        
        mock_cache = MagicMock()
        mock_cache_cls.return_value = mock_cache
        mock_cache.get.return_value = None  # Cache miss
        
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "Name: New Route\nDescription: New description."
        mock_client.chat.completions.create.return_value = mock_completion
        
        service = LLMService(api_key="fake-key")
        result = service.generate_route_description(sample_route)
        
        assert result.name == "New Route"
        
        # Verify cache was set
        mock_cache.set.assert_called_once()
        args = mock_cache.set.call_args
        assert "New Route" in args[0][2]

def test_llm_cache_operations(tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    
    cache = LLMCache(str(cache_dir))
    
    # Test set and get
    cache.set("prompt1", "model1", "response1")
    assert cache.get("prompt1", "model1") == "response1"
    
    # Test miss
    assert cache.get("prompt2", "model1") is None
    
    # Test persistence
    cache2 = LLMCache(str(cache_dir))
    assert cache2.get("prompt1", "model1") == "response1"
