import pytest
from unittest.mock import MagicMock, patch
from openai import OpenAIError

from pathypotomus.services.llm import LLMService
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

def test_generate_route_description_success(sample_route):
    with patch('pathypotomus.services.llm.OpenAI') as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "Name: Scenic Route\nDescription: A beautiful drive along the coast."
        mock_client.chat.completions.create.return_value = mock_completion
        
        service = LLMService(api_key="fake-key")
        result = service.generate_route_description(sample_route)
        
        assert result.name == "Scenic Route"
        assert result.description == "A beautiful drive along the coast."
        
        # Verify prompt construction
        call_args = mock_client.chat.completions.create.call_args
        assert call_args is not None
        messages = call_args[1]['messages']
        user_message = messages[1]['content']
        assert "via Main St" in user_message
        assert "Main St, First Ave" in user_message

def test_generate_route_description_openai_error(sample_route):
    with patch('pathypotomus.services.llm.OpenAI') as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        
        mock_client.chat.completions.create.side_effect = OpenAIError("API Error")
        
        service = LLMService(api_key="fake-key")
        
        # Should NOT raise, but return unmodified route
        result = service.generate_route_description(sample_route)
        
        assert result == sample_route
        assert result.name is None
