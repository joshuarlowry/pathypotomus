"""Configuration management for Pathypotomus."""
import os
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, ConfigDict


class Config(BaseModel):
    """Application configuration model with validation."""
    
    # Required configuration
    origin_addr: str = Field(..., description="Origin address for route planning")
    dest_addr: str = Field(..., description="Destination address for route planning")
    
    # Optional configuration with defaults
    osrm_url: str = Field(
        default="https://router.project-osrm.org",
        description="OSRM server URL"
    )
    llm_api_key: Optional[str] = Field(
        default=None,
        description="API key for LLM service"
    )
    llm_model: str = Field(
        default="gpt-3.5-turbo",
        description="LLM model to use"
    )
    llm_provider: str = Field(
        default="openai",
        description="LLM provider"
    )
    output_path: str = Field(
        default="./output/routes.html",
        description="Output path for generated HTML"
    )
    output_title: str = Field(
        default="Route Options",
        description="Title for generated HTML"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    enable_debug_mode: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    max_routes: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of routes to generate"
    )
    request_timeout: int = Field(
        default=30,
        ge=1,
        description="Request timeout in seconds"
    )
    
    model_config = ConfigDict(env_prefix="", case_sensitive=False)
        
    @field_validator('origin_addr', 'dest_addr')
    @classmethod
    def validate_addresses(cls, v):
        """Validate that addresses are not empty."""
        if not v or not v.strip():
            raise ValueError("Address cannot be empty")
        return v.strip()
    
    @field_validator('osrm_url')
    @classmethod
    def validate_osrm_url(cls, v):
        """Validate OSRM URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("OSRM URL must start with http:// or https://")
        return v
    
    @field_validator('output_path')
    @classmethod
    def validate_output_path(cls, v):
        """Validate output path."""
        if not v:
            raise ValueError("Output path cannot be empty")
        # Ensure directory exists
        output_dir = Path(v).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        return v


def load_config(env_file: Optional[str] = None) -> Config:
    """
    Load configuration from environment variables and .env file.
    
    Environment variables take precedence over .env file values.
    
    Args:
        env_file: Path to .env file. If None, uses default locations.
        
    Returns:
        Config: Validated configuration object
        
    Raises:
        ValidationError: If configuration is invalid
    """
    # First, collect values from .env file
    env_file_values = {}
    
    if env_file:
        if Path(env_file).exists():
            # Load env file values without setting environment variables
            from dotenv import dotenv_values
            env_file_values = dotenv_values(env_file)
    else:
        # Try default .env file locations
        from dotenv import dotenv_values
        for env_path in ['.env', '.env.dev', '.env.local']:
            if Path(env_path).exists():
                env_file_values = dotenv_values(env_path)
                break
    
    # Extract configuration from environment variables and file values
    config_data = {}
    
    # Map environment variables to config fields
    env_mapping = {
        'ORIGIN_ADDR': 'origin_addr',
        'DEST_ADDR': 'dest_addr',
        'OSRM_URL': 'osrm_url',
        'LLM_API_KEY': 'llm_api_key',
        'LLM_MODEL': 'llm_model',
        'LLM_PROVIDER': 'llm_provider',
        'OUTPUT_PATH': 'output_path',
        'OUTPUT_TITLE': 'output_title',
        'LOG_LEVEL': 'log_level',
        'ENABLE_DEBUG_MODE': 'enable_debug_mode',
        'MAX_ROUTES': 'max_routes',
        'REQUEST_TIMEOUT': 'request_timeout',
    }
    
    for env_var, config_key in env_mapping.items():
        # Environment variables take precedence over file values
        value = os.getenv(env_var) or env_file_values.get(env_var)
        
        if value is not None:
            # Convert string values to appropriate types
            if config_key in ['enable_debug_mode']:
                config_data[config_key] = value.lower() in ('true', '1', 'yes', 'on')
            elif config_key in ['max_routes', 'request_timeout']:
                try:
                    config_data[config_key] = int(value)
                except ValueError:
                    raise ValueError(f"Invalid integer value for {env_var}: {value}")
            else:
                config_data[config_key] = value
    
    return Config(**config_data)