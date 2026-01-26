import os
import pytest
from unittest.mock import patch, mock_open

from pathypotomus.config import Config, load_config

def test_config_defaults():
    config = Config(origin_addr="A", dest_addr="B")
    assert config.origin_addr == "A"
    assert config.dest_addr == "B"
    assert config.osrm_url == "https://router.project-osrm.org"
    assert config.llm_model == "google/gemini-flash-1.5"
    assert config.llm_provider == "openrouter"
    assert config.cache_dir == ".cache"

def test_config_validation_valid():
    config = Config(
        origin_addr="Chicago, IL",
        dest_addr="Milwaukee, WI",
        max_routes=5
    )
    assert config.origin_addr == "Chicago, IL"
    assert config.max_routes == 5

def test_config_validation_invalid_address():
    with pytest.raises(ValueError, match="Address cannot be empty"):
        Config(origin_addr="", dest_addr="B")

def test_config_validation_invalid_url():
    with pytest.raises(ValueError, match="OSRM URL must start"):
        Config(origin_addr="A", dest_addr="B", osrm_url="ftp://example.com")

def test_load_config_from_env_vars():
    with patch.dict(os.environ, {
        "ORIGIN_ADDR": "San Francisco, CA",
        "DEST_ADDR": "Los Angeles, CA",
        "MAX_ROUTES": "2",
        "OPENROUTER_API_KEY": "sk-test",
        "CACHE_DIR": "/tmp/cache"
    }, clear=True):
        config = load_config()
        assert config.origin_addr == "San Francisco, CA"
        assert config.dest_addr == "Los Angeles, CA"
        assert config.max_routes == 2
        assert config.llm_api_key == "sk-test"
        assert config.cache_dir == "/tmp/cache"
