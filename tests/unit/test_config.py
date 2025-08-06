"""Tests for configuration management."""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from pathypotomus.config import Config, load_config


class TestConfig:
    """Test configuration model validation."""

    def test_valid_config(self):
        """Test valid configuration creation."""
        config = Config(
            origin_addr="123 Main St, Springfield, IL",
            dest_addr="456 Oak Ave, Shelbyville, IL",
            osrm_url="https://router.project-osrm.org",
            llm_api_key="test-key",
            llm_model="gpt-3.5-turbo",
            output_path="./output/routes.html",
            log_level="INFO",
            max_routes=3,
            request_timeout=30
        )
        
        assert config.origin_addr == "123 Main St, Springfield, IL"
        assert config.dest_addr == "456 Oak Ave, Shelbyville, IL"
        assert config.osrm_url == "https://router.project-osrm.org"
        assert config.llm_api_key == "test-key"
        assert config.llm_model == "gpt-3.5-turbo"
        assert config.max_routes == 3
        assert config.request_timeout == 30

    def test_missing_required_fields(self):
        """Test validation error for missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            Config()
        
        errors = exc_info.value.errors()
        error_fields = {error['loc'][0] for error in errors}
        assert 'origin_addr' in error_fields
        assert 'dest_addr' in error_fields

    def test_invalid_log_level(self):
        """Test validation error for invalid log level."""
        with pytest.raises(ValidationError) as exc_info:
            Config(
                origin_addr="123 Main St",
                dest_addr="456 Oak Ave",
                log_level="INVALID"
            )
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'log_level' for error in errors)

    def test_invalid_max_routes(self):
        """Test validation error for invalid max_routes."""
        with pytest.raises(ValidationError) as exc_info:
            Config(
                origin_addr="123 Main St",
                dest_addr="456 Oak Ave",
                max_routes=0
            )
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'max_routes' for error in errors)

    def test_invalid_request_timeout(self):
        """Test validation error for invalid request_timeout."""
        with pytest.raises(ValidationError) as exc_info:
            Config(
                origin_addr="123 Main St",
                dest_addr="456 Oak Ave",
                request_timeout=-1
            )
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'request_timeout' for error in errors)

    def test_default_values(self):
        """Test default values are applied correctly."""
        config = Config(
            origin_addr="123 Main St",
            dest_addr="456 Oak Ave"
        )
        
        assert config.osrm_url == "https://router.project-osrm.org"
        assert config.llm_model == "gpt-3.5-turbo"
        assert config.llm_provider == "openai"
        assert config.output_path == "./output/routes.html"
        assert config.log_level == "INFO"
        assert config.max_routes == 3
        assert config.request_timeout == 30
        assert config.enable_debug_mode is False


class TestLoadConfig:
    """Test configuration loading from environment and files."""

    def test_load_from_environment(self):
        """Test loading configuration from environment variables."""
        env_vars = {
            'ORIGIN_ADDR': '123 Main St, Test City',
            'DEST_ADDR': '456 Oak Ave, Test City',
            'OSRM_URL': 'http://localhost:5000',
            'LLM_API_KEY': 'test-api-key',
            'LLM_MODEL': 'gpt-4',
            'LOG_LEVEL': 'DEBUG',
            'MAX_ROUTES': '5',
            'REQUEST_TIMEOUT': '60'
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            config = load_config()
        
        assert config.origin_addr == '123 Main St, Test City'
        assert config.dest_addr == '456 Oak Ave, Test City'
        assert config.osrm_url == 'http://localhost:5000'
        assert config.llm_api_key == 'test-api-key'
        assert config.llm_model == 'gpt-4'
        assert config.log_level == 'DEBUG'
        assert config.max_routes == 5
        assert config.request_timeout == 60

    def test_load_from_env_file(self):
        """Test loading configuration from .env file."""
        env_content = """
ORIGIN_ADDR="123 Main St, File City"
DEST_ADDR="456 Oak Ave, File City"
LLM_API_KEY="file-api-key"
LOG_LEVEL="WARNING"
        """.strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file_path = f.name
        
        try:
            config = load_config(env_file=env_file_path)
            
            assert config.origin_addr == "123 Main St, File City"
            assert config.dest_addr == "456 Oak Ave, File City"
            assert config.llm_api_key == "file-api-key"
            assert config.log_level == "WARNING"
        finally:
            os.unlink(env_file_path)

    def test_missing_required_config_raises_error(self):
        """Test that missing required configuration raises clear error."""
        # Clear environment variables that might be set
        env_vars_to_clear = ['ORIGIN_ADDR', 'DEST_ADDR']
        
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                load_config()
            
            errors = exc_info.value.errors()
            error_fields = {error['loc'][0] for error in errors}
            assert 'origin_addr' in error_fields
            assert 'dest_addr' in error_fields

    def test_env_file_not_found_uses_defaults(self):
        """Test that non-existent env file doesn't cause errors."""
        env_vars = {
            'ORIGIN_ADDR': '123 Main St',
            'DEST_ADDR': '456 Oak Ave'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config(env_file="nonexistent.env")
            
            assert config.origin_addr == "123 Main St"
            assert config.dest_addr == "456 Oak Ave"
            # Should use defaults for other values
            assert config.osrm_url == "https://router.project-osrm.org"

    def test_environment_overrides_env_file(self):
        """Test that environment variables override .env file values."""
        env_content = """
ORIGIN_ADDR="File Origin"
DEST_ADDR="File Destination"
LOG_LEVEL="ERROR"
        """.strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file_path = f.name
        
        try:
            env_vars = {
                'ORIGIN_ADDR': 'Env Origin',
                'LOG_LEVEL': 'DEBUG'
            }
            
            with patch.dict(os.environ, env_vars, clear=False):
                config = load_config(env_file=env_file_path)
            
            # Environment should override file
            assert config.origin_addr == "Env Origin"
            assert config.log_level == "DEBUG"
            # File value should be used where env var not set
            assert config.dest_addr == "File Destination"
        finally:
            os.unlink(env_file_path)