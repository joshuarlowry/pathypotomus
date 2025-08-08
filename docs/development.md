# Development Guidelines

Comprehensive guide for contributing to and developing the LLM-Powered Route Planner.

## 🚀 Getting Started

### Development Environment Setup

1. **Prerequisites:**
   ```bash
   # Required
   Python 3.9+
   Docker & Docker Compose
   Git
   
   # Recommended
   VS Code or PyCharm
   Python virtual environment manager (venv, conda, or poetry)
   ```

2. **Local Setup:**
   ```bash
   # Clone repository
   git clone https://github.com/your-org/pathypotomus.git
   cd pathypotomus
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   
   # Install pre-commit hooks
   pre-commit install
   
   # Copy environment template
   cp .env.example .env.dev
   ```

3. **Development Configuration:**
   ```bash
   # .env.dev - Development settings
   ORIGIN_ADDR="123 Main St, Springfield, IL"
   DEST_ADDR="456 Oak Ave, Shelbyville, IL"
   OSRM_URL="https://router.project-osrm.org"  # Use public for dev
   LLM_API_KEY="your-dev-api-key"
   OUTPUT_PATH="./dev-output/routes.html"
   LOG_LEVEL="DEBUG"
   ENABLE_DEBUG_MODE=true
   ```

### Project Structure

```
pathypotomus/
├── src/pathypotomus/           # Main application code
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration management
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── coordinates.py
│   │   ├── route.py
│   │   └── config.py
│   ├── services/               # Service layer
│   │   ├── __init__.py
│   │   ├── geocoding.py
│   │   ├── osrm.py
│   │   ├── llm.py
│   │   └── html_generator.py
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── polyline.py
│       └── logging.py
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── fixtures/               # Test data
├── templates/                  # HTML templates
│   └── route_map.html
├── docs/                       # Documentation
├── scripts/                    # Development scripts
├── docker-compose.yml          # Docker services
├── docker-compose.dev.yml      # Development overrides
├── Dockerfile
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── pyproject.toml             # Project configuration
├── .pre-commit-config.yaml    # Pre-commit hooks
└── README.md
```

## 🏗️ Architecture Guidelines

### Code Organization

1. **Layered Architecture:**
   ```
   Presentation Layer (CLI/HTML Output)
        ↓
   Service Layer (Business Logic)
        ↓
   Data Layer (Models & External APIs)
   ```

2. **Dependency Injection:**
   ```python
   # Good: Inject dependencies
   class RouteService:
       def __init__(self, osrm_client: OSRMClient, llm_service: LLMService):
           self.osrm_client = osrm_client
           self.llm_service = llm_service
   
   # Avoid: Hard-coded dependencies
   class RouteService:
       def __init__(self):
           self.osrm_client = OSRMClient()  # Hard-coded
   ```

3. **Interface Segregation:**
   ```python
   # Define clear interfaces
   from abc import ABC, abstractmethod
   
   class GeocodingService(ABC):
       @abstractmethod
       async def geocode(self, address: str) -> Coordinates:
           pass
   ```

### Design Patterns

1. **Factory Pattern for Services:**
   ```python
   class ServiceFactory:
       @staticmethod
       def create_geocoding_service(provider: str) -> GeocodingService:
           if provider == "nominatim":
               return NominatimGeocodingService()
           elif provider == "google":
               return GoogleGeocodingService()
           else:
               raise ValueError(f"Unknown provider: {provider}")
   ```

2. **Strategy Pattern for LLM Providers:**
   ```python
   class LLMProvider(ABC):
       @abstractmethod
       async def generate_text(self, prompt: str) -> str:
           pass
   
   class OpenAIProvider(LLMProvider):
       async def generate_text(self, prompt: str) -> str:
           # OpenAI implementation
           pass
   ```

3. **Builder Pattern for Configuration:**
   ```python
   class ConfigBuilder:
       def __init__(self):
           self._config = {}
       
       def origin(self, address: str) -> 'ConfigBuilder':
           self._config['origin_addr'] = address
           return self
       
       def build(self) -> AppConfig:
           return AppConfig(**self._config)
   ```

## 🧪 Testing Strategy

### Test Structure

1. **Unit Tests:**
   ```python
   # tests/unit/test_coordinates.py
   import pytest
   from pathypotomus.models.coordinates import Coordinates
   
   class TestCoordinates:
       def test_valid_coordinates(self):
           coords = Coordinates(41.8781, -87.6298)
           assert coords.validate() is True
       
       def test_invalid_latitude(self):
           with pytest.raises(ValueError):
               Coordinates(91.0, 0.0)  # Invalid latitude
       
       def test_distance_calculation(self):
           chicago = Coordinates(41.8781, -87.6298)
           milwaukee = Coordinates(43.0389, -87.9065)
           distance = chicago.distance_to(milwaukee)
           assert 120 < distance < 140  # Approximate distance in km
   ```

2. **Integration Tests:**
   ```python
   # tests/integration/test_route_generation.py
   import pytest
   from pathypotomus.services.route_service import RouteService
   
   @pytest.mark.integration
   class TestRouteGeneration:
       @pytest.fixture
       def route_service(self):
           # Use real services with test configuration
           return RouteService(
               osrm_client=OSRMClient("https://router.project-osrm.org"),
               llm_service=MockLLMService()  # Use mock for LLM to avoid costs
           )
       
       async def test_generate_routes_end_to_end(self, route_service):
           origin = Coordinates(41.8781, -87.6298)
           destination = Coordinates(42.3601, -71.0589)
           
           routes = await route_service.generate_routes(origin, destination)
           
           assert len(routes) >= 1
           assert all(route.distance > 0 for route in routes)
           assert all(route.duration > 0 for route in routes)
   ```

3. **Test Fixtures:**
   ```python
   # tests/fixtures/routes.py
   import pytest
   from pathypotomus.models.route import Route
   from pathypotomus.models.coordinates import Coordinates
   
   @pytest.fixture
   def sample_route():
       return Route(
           geometry=[
               Coordinates(41.8781, -87.6298),
               Coordinates(41.8800, -87.6300),
               Coordinates(41.8850, -87.6350)
           ],
           distance=5000.0,  # 5km
           duration=600.0,   # 10 minutes
           summary="via Lake Shore Drive",
           major_roads=["Lake Shore Drive", "Michigan Avenue"]
       )
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pathypotomus --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests (requires services)
pytest tests/integration/ -m integration

# Run specific test file
pytest tests/unit/test_coordinates.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Test Configuration

```python
# pytest.ini
[tool:pytest]
minversion = 6.0
addopts = -ra -q --strict-markers
testpaths = tests
markers =
    integration: marks tests as integration tests (may be slow)
    unit: marks tests as unit tests (fast)
    llm: marks tests that require LLM API access
    osrm: marks tests that require OSRM service
```

## 📝 Code Standards

### Python Style Guide

1. **Follow PEP 8:**
   ```python
   # Good
   def calculate_route_distance(coordinates: List[Coordinates]) -> float:
       """Calculate total distance for a route."""
       total_distance = 0.0
       for i in range(len(coordinates) - 1):
           total_distance += coordinates[i].distance_to(coordinates[i + 1])
       return total_distance
   
   # Avoid
   def calcDist(coords):
       d=0
       for i in range(len(coords)-1):
           d+=coords[i].distance_to(coords[i+1])
       return d
   ```

2. **Type Hints:**
   ```python
   from typing import List, Optional, Dict, Any
   
   def process_routes(
       routes: List[Route], 
       config: AppConfig
   ) -> Dict[str, Any]:
       """Process routes with proper type hints."""
       pass
   ```

3. **Docstrings:**
   ```python
   def geocode_address(address: str, provider: str = "nominatim") -> Coordinates:
       """
       Convert address to coordinates using specified provider.
       
       Args:
           address: Street address to geocode
           provider: Geocoding provider to use ('nominatim', 'google')
           
       Returns:
           Coordinates object with lat/lon
           
       Raises:
           GeocodingError: If address cannot be geocoded
           ValueError: If provider is not supported
           
       Example:
           >>> coords = geocode_address("123 Main St, Chicago, IL")
           >>> print(f"Lat: {coords.lat}, Lon: {coords.lon}")
       """
       pass
   ```

### Code Quality Tools

1. **Pre-commit Configuration:**
   ```yaml
   # .pre-commit-config.yaml
   repos:
     - repo: https://github.com/psf/black
       rev: 23.1.0
       hooks:
         - id: black
           language_version: python3.9
   
     - repo: https://github.com/pycqa/isort
       rev: 5.12.0
       hooks:
         - id: isort
           args: ["--profile", "black"]
   
     - repo: https://github.com/pycqa/flake8
       rev: 6.0.0
       hooks:
         - id: flake8
           args: [--max-line-length=88, --extend-ignore=E203]
   
     - repo: https://github.com/pre-commit/mirrors-mypy
       rev: v1.0.1
       hooks:
         - id: mypy
           additional_dependencies: [types-requests]
   ```

2. **Linting Commands:**
   ```bash
   # Format code
   black src/ tests/
   
   # Sort imports
   isort src/ tests/
   
   # Check style
   flake8 src/ tests/
   
   # Type checking
   mypy src/
   
   # Run all checks
   pre-commit run --all-files
   ```

## 🔧 Development Workflow

### Git Workflow

1. **Branch Naming:**
   ```bash
   # Feature branches
   git checkout -b feature/llm-integration
   git checkout -b feature/osrm-client
   
   # Bug fixes
   git checkout -b fix/geocoding-error-handling
   
   # Documentation
   git checkout -b docs/api-specifications
   ```

2. **Commit Messages:**
   ```bash
   # Good commit messages
   git commit -m "feat: add OpenAI LLM service integration"
   git commit -m "fix: handle OSRM timeout errors gracefully"
   git commit -m "docs: update deployment guide with SSL setup"
   git commit -m "test: add unit tests for coordinate validation"
   
   # Follow conventional commits format
   # type(scope): description
   ```

3. **Pull Request Process:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement
   
   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   ```

### Development Commands

```bash
# Development server with auto-reload
python -m pathypotomus.main --dev --watch

# Run with debug logging
LOG_LEVEL=DEBUG python -m pathypotomus.main

# Generate sample routes for testing
python scripts/generate_sample_routes.py

# Validate configuration
python -m pathypotomus.config --validate

# Run performance benchmarks
python scripts/benchmark.py
```

## 🐛 Debugging

### Logging Configuration

```python
# src/pathypotomus/utils/logging.py
import logging
import sys
from pathlib import Path

def setup_logging(level: str = "INFO", log_file: Optional[Path] = None):
    """Configure application logging."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File handler (optional)
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=handlers
    )
```

### Debug Mode

```python
# Enable debug features in development
if config.debug_mode:
    # Save intermediate data
    with open("debug/osrm_response.json", "w") as f:
        json.dump(osrm_response, f, indent=2)
    
    # Add debug routes to map
    debug_routes = generate_debug_routes()
    
    # Extended logging
    logger.debug(f"Processing {len(routes)} routes")
    logger.debug(f"LLM tokens used: {token_count}")
```

### Common Debug Scenarios

1. **OSRM Issues:**
   ```python
   # Add request/response logging
   logger.debug(f"OSRM Request: {osrm_url}")
   logger.debug(f"OSRM Response: {response.status_code}")
   logger.debug(f"OSRM Data: {response.json()}")
   ```

2. **LLM Issues:**
   ```python
   # Log prompts and responses
   logger.debug(f"LLM Prompt: {prompt}")
   logger.debug(f"LLM Response: {response}")
   logger.debug(f"Tokens used: {response.usage}")
   ```

3. **Geocoding Issues:**
   ```python
   # Test geocoding separately
   coords = await geocoding_service.geocode("123 Main St")
   logger.debug(f"Geocoded to: {coords}")
   ```

## 📚 Documentation

### Documentation Standards

1. **API Documentation:**
   ```python
   # Use docstrings for all public methods
   def generate_routes(self, origin: str, destination: str) -> List[EnrichedRoute]:
       """
       Generate route alternatives with AI descriptions.
       
       This method coordinates between the routing engine and LLM service
       to produce route alternatives with human-friendly names and descriptions.
       
       Args:
           origin: Starting address or coordinates
           destination: Ending address or coordinates
           
       Returns:
           List of routes with AI-generated names and descriptions
           
       Raises:
           GeocodingError: If addresses cannot be converted to coordinates
           RoutingError: If route calculation fails
           LLMError: If description generation fails
           
       Example:
           >>> service = RouteService(osrm_client, llm_service)
           >>> routes = await service.generate_routes(
           ...     "Chicago, IL", 
           ...     "Milwaukee, WI"
           ... )
           >>> print(f"Found {len(routes)} route alternatives")
       """
   ```

2. **README Updates:**
   - Keep installation instructions current
   - Update feature list as development progresses
   - Include troubleshooting for common issues

3. **Changelog:**
   ```markdown
   # Changelog
   
   ## [Unreleased]
   ### Added
   - Support for multiple LLM providers
   - Route caching for improved performance
   
   ### Changed
   - Improved error handling in OSRM client
   
   ### Fixed
   - Geocoding timeout issues
   
   ## [1.0.0] - 2024-01-15
   ### Added
   - Initial MVP release
   - OSRM integration
   - OpenAI LLM integration
   - Static HTML output
   ```

## 🚀 Release Process

### Version Management

```bash
# Update version
bump2version patch  # 1.0.0 -> 1.0.1
bump2version minor  # 1.0.1 -> 1.1.0
bump2version major  # 1.1.0 -> 2.0.0
```

### Release Checklist

1. **Pre-release:**
   - [ ] All tests pass
   - [ ] Documentation updated
   - [ ] Changelog updated
   - [ ] Version bumped
   - [ ] Dependencies updated

2. **Release:**
   - [ ] Create release branch
   - [ ] Tag release
   - [ ] Build Docker images
   - [ ] Update deployment docs

3. **Post-release:**
   - [ ] Merge to main
   - [ ] Deploy to production
   - [ ] Monitor for issues
   - [ ] Update project board

## 🤝 Contributing

### First-Time Contributors

1. **Good First Issues:**
   - Documentation improvements
   - Additional test cases
   - Error message improvements
   - Configuration validation

2. **Getting Help:**
   - Check existing issues and discussions
   - Join development Discord/Slack
   - Ask questions in pull requests

### Code Review Guidelines

1. **For Authors:**
   - Keep PRs focused and small
   - Write descriptive commit messages
   - Include tests for new features
   - Update documentation

2. **For Reviewers:**
   - Be constructive and helpful
   - Focus on code quality and maintainability
   - Check for security issues
   - Verify tests cover new functionality

### Community Guidelines

- Be respectful and inclusive
- Help newcomers get started
- Share knowledge and best practices
- Report bugs and suggest improvements

This development guide provides the foundation for maintaining high code quality and smooth collaboration on the LLM-Powered Route Planner project.

## 🧭 OSRM Routing Notes

- Implemented `pathypotomus.services.osrm.OSRMService` with:
  - URL shape: `/route/v1/driving/{lon1},{lat1};{lon2},{lat2}`
  - Params: `alternatives=true|false`, `overview=simplified`, `steps=true`, `geometries=polyline`
  - Polyline decoding via `polyline` package
  - Major roads extracted from legs[].steps[].name (deduped, max 5)
  - Summary generated: `Local roads` | `via <road>` | `via <road> and N other roads`
- Error handling:
  - Non-200 HTTP → `RoutingError`
  - OSRM `code != 'Ok'` → `RoutingError`
- Testing strategy:
  - Async unit tests with a fake aiohttp-like session/response
  - Validate params, decoding, limits, and error paths
  - Keep `PYTHONPATH=/workspace/src` when running tests locally

## 🤖 Future LLM Integration Notes

- Mocking:
  - Provide `MockLLMService` returning deterministic name/description tuples
  - Guard for token/length constraints; truncate at 50/150 chars respectively
- Concurrency:
  - Use `asyncio.gather` to parallelize calls per route; set `return_exceptions=True`
  - Collect per-route fallbacks when exceptions occur; do not fail the batch
- Fallbacks:
  - On LLM errors: name = `Route {i}`, description = `{distance_km} km ({duration_formatted}) [via {first_road}]`
  - Consider caching descriptions keyed by route hash (geometry + summary)
- Observability:
  - Log prompts and model, but redact PII; include timing and retries
  - Add counters: successes, fallbacks, avg latency
- Configuration:
  - `LLM_PROVIDER`, `LLM_MODEL`, timeouts, and per-request max tokens in config
- Testing:
  - Unit: prompt builders, validation, truncation
  - Integration (optional): gated tests using live API with `-m llm` marker