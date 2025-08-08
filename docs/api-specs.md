# API Specifications

Detailed API specifications and data models for the LLM-Powered Route Planner.

## 📋 Overview

This document defines the internal APIs, data models, and interfaces between system components. While the MVP doesn't expose external APIs, these specifications guide the internal architecture and future API development.

## 🔧 Core Data Models

### Coordinates

Represents geographic coordinates with validation.

```python
@dataclass
class Coordinates:
    lat: float
    lon: float
    
    def __post_init__(self):
        if not self.validate():
            raise ValueError(f"Invalid coordinates: {self.lat}, {self.lon}")
    
    def validate(self) -> bool:
        """Validate coordinate ranges"""
        return -90 <= self.lat <= 90 and -180 <= self.lon <= 180
    
    def distance_to(self, other: 'Coordinates') -> float:
        """Calculate distance in kilometers using Haversine formula"""
        # Implementation details...
        pass
    
    def __str__(self) -> str:
        return f"{self.lat},{self.lon}"

# JSON Schema
{
    "type": "object",
    "properties": {
        "lat": {"type": "number", "minimum": -90, "maximum": 90},
        "lon": {"type": "number", "minimum": -180, "maximum": 180}
    },
    "required": ["lat", "lon"]
}
```

### Route

Core route data structure with geometry and metadata.

```python
@dataclass
class Route:
    geometry: List[Coordinates]
    distance: float  # meters
    duration: float  # seconds
    summary: str
    major_roads: List[str]
    route_id: Optional[str] = None
    
    @property
    def distance_km(self) -> float:
        """Distance in kilometers"""
        return round(self.distance / 1000, 1)
    
    @property
    def duration_minutes(self) -> int:
        """Duration in minutes"""
        return int(self.duration / 60)
    
    @property
    def duration_formatted(self) -> str:
        """Human-readable duration"""
        minutes = self.duration_minutes
        if minutes < 60:
            return f"{minutes}m"
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
    
    def get_bounds(self) -> Tuple[Coordinates, Coordinates]:
        """Get bounding box for the route"""
        lats = [coord.lat for coord in self.geometry]
        lons = [coord.lon for coord in self.geometry]
        return (
            Coordinates(min(lats), min(lons)),  # Southwest
            Coordinates(max(lats), max(lons))   # Northeast
        )

# JSON Schema
{
    "type": "object",
    "properties": {
        "geometry": {
            "type": "array",
            "items": {"$ref": "#/definitions/Coordinates"}
        },
        "distance": {"type": "number", "minimum": 0},
        "duration": {"type": "number", "minimum": 0},
        "summary": {"type": "string"},
        "major_roads": {
            "type": "array",
            "items": {"type": "string"}
        },
        "route_id": {"type": "string", "nullable": true}
    },
    "required": ["geometry", "distance", "duration", "summary", "major_roads"]
}
```

### EnrichedRoute

Route with AI-generated name and description.

```python
@dataclass
class EnrichedRoute:
    # Inherit all Route fields
    geometry: List[Coordinates]
    distance: float
    duration: float
    summary: str
    major_roads: List[str]
    route_id: Optional[str] = None
    
    # AI-generated content
    name: str
    description: str
    color: str
    
    @classmethod
    def from_route(cls, route: Route, name: str, description: str, color: str) -> 'EnrichedRoute':
        """Create EnrichedRoute from base Route"""
        return cls(
            geometry=route.geometry,
            distance=route.distance,
            duration=route.duration,
            summary=route.summary,
            major_roads=route.major_roads,
            route_id=route.route_id,
            name=name,
            description=description,
            color=color
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'description': self.description,
            'distance_km': self.distance_km,
            'duration_formatted': self.duration_formatted,
            'major_roads': self.major_roads,
            'color': self.color,
            'geometry': [{'lat': c.lat, 'lon': c.lon} for c in self.geometry]
        }

# JSON Schema
{
    "allOf": [
        {"$ref": "#/definitions/Route"},
        {
            "type": "object",
            "properties": {
                "name": {"type": "string", "maxLength": 50},
                "description": {"type": "string", "maxLength": 150},
                "color": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"}
            },
            "required": ["name", "description", "color"]
        }
    ]
}
```

### Configuration Models

```python
@dataclass
class AppConfig:
    # Required
    origin_addr: str
    dest_addr: str
    
    # Optional with defaults
    osrm_url: str = "https://router.project-osrm.org"
    llm_api_key: Optional[str] = None
    llm_model: str = "gpt-3.5-turbo"
    output_path: str = "routes.html"
    max_routes: int = 3
    
    # Advanced options
    geocoding_provider: str = "nominatim"
    map_zoom: int = 12
    route_colors: List[str] = field(default_factory=lambda: ["#e74c3c", "#3498db", "#2ecc71"])
    
    def validate(self) -> List[str]:
        """Return list of validation errors"""
        errors = []
        if not self.origin_addr.strip():
            errors.append("origin_addr is required")
        if not self.dest_addr.strip():
            errors.append("dest_addr is required")
        if self.max_routes < 1 or self.max_routes > 5:
            errors.append("max_routes must be between 1 and 5")
        if len(self.route_colors) < self.max_routes:
            errors.append("Not enough route colors for max_routes")
        return errors

@dataclass
class RouteRequest:
    origin: Coordinates
    destination: Coordinates
    alternatives: bool = True
    profile: str = "driving"
    max_alternatives: int = 3
```

## 🌐 Service Interfaces

### GeocodingService

Interface for address-to-coordinate conversion.

```python
from abc import ABC, abstractmethod

class GeocodingService(ABC):
    """Abstract base class for geocoding services"""
    
    @abstractmethod
    async def geocode(self, address: str) -> Coordinates:
        """Convert address to coordinates"""
        pass
    
    @abstractmethod
    async def reverse_geocode(self, coords: Coordinates) -> str:
        """Convert coordinates to address"""
        pass

class NominatimGeocodingService(GeocodingService):
    """OpenStreetMap Nominatim geocoding service"""
    
    def __init__(self, base_url: str = "https://nominatim.openstreetmap.org"):
        self.base_url = base_url
        self.session = aiohttp.ClientSession()
    
    async def geocode(self, address: str) -> Coordinates:
        """
        Geocode address using Nominatim API
        
        Args:
            address: Street address to geocode
            
        Returns:
            Coordinates object
            
        Raises:
            GeocodingError: If address cannot be geocoded
        """
        url = f"{self.base_url}/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise GeocodingError(f"Geocoding failed: HTTP {response.status}")
            
            data = await response.json()
            if not data:
                raise GeocodingError(f"Address not found: {address}")
            
            result = data[0]
            return Coordinates(
                lat=float(result['lat']),
                lon=float(result['lon'])
            )
    
    async def reverse_geocode(self, coords: Coordinates) -> str:
        """Reverse geocode coordinates to address"""
        url = f"{self.base_url}/reverse"
        params = {
            'lat': coords.lat,
            'lon': coords.lon,
            'format': 'json'
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise GeocodingError(f"Reverse geocoding failed: HTTP {response.status}")
            
            data = await response.json()
            return data.get('display_name', f"{coords.lat},{coords.lon}")

# Custom Exceptions
class GeocodingError(Exception):
    """Raised when geocoding operations fail"""
    pass
```

### OSRMService

Interface for route calculations using OSRM.

```python
class OSRMService:
    """OSRM routing service client"""
    
    def __init__(self, base_url: str = "https://router.project-osrm.org", session: Optional[aiohttp.ClientSession] = None):
        self.base_url = base_url.rstrip('/')
        self.session = session or aiohttp.ClientSession()
    
    async def get_routes(self, origin: Coordinates, destination: Coordinates, 
                        alternatives: bool = True, max_alternatives: int = 3) -> List[Route]:
        """
        Get route alternatives from OSRM
        
        Args:
            origin: Starting coordinates
            destination: Ending coordinates
            alternatives: Whether to request alternative routes
            max_alternatives: Maximum number of alternatives to return
            
        Returns:
            List of Route objects
            
        Raises:
            RoutingError: If routing request fails
        """
        # Build OSRM URL
        coords = f"{origin.lon},{origin.lat};{destination.lon},{destination.lat}"
        url = f"{self.base_url}/route/v1/driving/{coords}"
        
        params = {
            'alternatives': 'true' if alternatives else 'false',
            'overview': 'simplified',
            'steps': 'true',
            'geometries': 'polyline'
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise RoutingError(f"OSRM request failed: HTTP {response.status}")
            
            data = await response.json()
            
            if data.get('code') != 'Ok':
                raise RoutingError(f"OSRM error: {data.get('message', 'Unknown error')}")
            
            routes = []
            osrm_routes = data.get('routes', [])[:max_alternatives]
            
            for i, osrm_route in enumerate(osrm_routes):
                route = self._parse_osrm_route(osrm_route, route_id=f"route_{i}")
                routes.append(route)
            
            return routes
    
    def _parse_osrm_route(self, osrm_route: dict, route_id: str) -> Route:
        """Parse OSRM route response into Route object"""
        # Decode polyline geometry
        geometry = self._decode_polyline(osrm_route['geometry'])
        
        # Extract major roads from steps
        major_roads = self._extract_major_roads(osrm_route.get('legs', []))
        
        return Route(
            geometry=geometry,
            distance=osrm_route['distance'],
            duration=osrm_route['duration'],
            summary=self._generate_summary(major_roads),
            major_roads=major_roads,
            route_id=route_id
        )
    
    def _decode_polyline(self, encoded: str) -> List[Coordinates]:
        """Decode OSRM polyline to coordinate list"""
        # Standard polyline decoding algorithm
        # Implementation details...
        pass
    
    def _extract_major_roads(self, legs: List[dict]) -> List[str]:
        """Extract major road names from OSRM steps"""
        roads = set()
        for leg in legs:
            for step in leg.get('steps', []):
                name = step.get('name', '').strip()
                if name and name != '' and len(name) > 2:
                    roads.add(name)
        return list(roads)[:5]  # Limit to top 5 roads
    
    def _generate_summary(self, major_roads: List[str]) -> str:
        """Generate route summary from major roads"""
        if not major_roads:
            return "Local roads"
        elif len(major_roads) == 1:
            return f"via {major_roads[0]}"
        else:
            return f"via {major_roads[0]} and {len(major_roads)-1} other roads"

# Custom Exceptions
class RoutingError(Exception):
    """Raised when routing operations fail"""
    pass
```

### LLMService

Interface for AI-powered route descriptions.

```python
class LLMService:
    """Large Language Model service for route descriptions"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def generate_route_descriptions(self, routes: List[Route]) -> List[Tuple[str, str]]:
        """
        Generate names and descriptions for multiple routes in parallel
        
        Args:
            routes: List of Route objects
            
        Returns:
            List of (name, description) tuples
            
        Raises:
            LLMError: If LLM generation fails
        """
        tasks = []
        for i, route in enumerate(routes):
            task = self._generate_single_route_description(route, i + 1)
            tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions in results
            descriptions = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Use fallback description
                    fallback = self._get_fallback_description(routes[i], i + 1)
                    descriptions.append(fallback)
                else:
                    descriptions.append(result)
            
            return descriptions
            
        except Exception as e:
            raise LLMError(f"Failed to generate route descriptions: {str(e)}")
    
    async def _generate_single_route_description(self, route: Route, route_number: int) -> Tuple[str, str]:
        """Generate name and description for a single route"""
        
        # Determine route characteristics
        route_type = self._classify_route(route)
        
        # Generate name
        name_prompt = self._build_name_prompt(route, route_type, route_number)
        name = await self._call_llm(name_prompt, max_tokens=20)
        
        # Generate description
        desc_prompt = self._build_description_prompt(route, name, route_type)
        description = await self._call_llm(desc_prompt, max_tokens=50)
        
        # Validate and clean outputs
        name = self._validate_name(name)
        description = self._validate_description(description)
        
        return (name, description)
    
    def _build_name_prompt(self, route: Route, route_type: str, route_number: int) -> str:
        """Build prompt for route name generation"""
        return f"""Generate a catchy, descriptive name for this driving route:

Route {route_number}:
- Distance: {route.distance_km} km
- Duration: {route.duration_formatted}
- Major roads: {', '.join(route.major_roads[:3])}
- Route type: {route_type}

Requirements:
- Under 50 characters
- Capture the route's character
- Be memorable and distinctive

Examples: "Highway Express", "Scenic Valley Route", "Downtown Dash"

Name:"""

    def _build_description_prompt(self, route: Route, name: str, route_type: str) -> str:
        """Build prompt for route description generation"""
        return f"""Write a brief description for this route:

Route: {name}
- Distance: {route.distance_km} km ({route.duration_formatted})
- Major roads: {', '.join(route.major_roads[:3])}
- Type: {route_type}

Requirements:
- 1-2 sentences, under 150 characters
- Highlight what makes this route unique
- Focus on practical benefits (speed, scenery, etc.)

Description:"""

    async def _call_llm(self, prompt: str, max_tokens: int = 50) -> str:
        """Make API call to LLM service"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise LLMError(f"LLM API call failed: {str(e)}")
    
    def _classify_route(self, route: Route) -> str:
        """Classify route type based on characteristics"""
        # Simple classification logic
        if any('highway' in road.lower() or 'interstate' in road.lower() 
               for road in route.major_roads):
            return "highway"
        elif route.distance_km < 5:
            return "local"
        elif any('scenic' in road.lower() or 'park' in road.lower() 
                 for road in route.major_roads):
            return "scenic"
        else:
            return "standard"
    
    def _validate_name(self, name: str) -> str:
        """Validate and clean route name"""
        name = name.strip().strip('"').strip("'")
        if len(name) > 50:
            name = name[:47] + "..."
        return name or "Route"
    
    def _validate_description(self, description: str) -> str:
        """Validate and clean route description"""
        description = description.strip().strip('"').strip("'")
        if len(description) > 150:
            description = description[:147] + "..."
        return description or "A driving route option."
    
    def _get_fallback_description(self, route: Route, route_number: int) -> Tuple[str, str]:
        """Generate fallback description when LLM fails"""
        name = f"Route {route_number}"
        description = f"{route.distance_km} km route taking {route.duration_formatted}"
        if route.major_roads:
            description += f" via {route.major_roads[0]}"
        return (name, description)

# Custom Exceptions
class LLMError(Exception):
    """Raised when LLM operations fail"""
    pass
```

### HTMLGenerator

Interface for generating static HTML output.

```python
class HTMLGenerator:
    """Generate static HTML output with embedded map"""
    
    def __init__(self, template_path: str = "templates/route_map.html"):
        self.template_path = template_path
        self.template = self._load_template()
    
    def generate_html(self, routes: List[EnrichedRoute], 
                     origin_addr: str, dest_addr: str) -> str:
        """
        Generate complete HTML output
        
        Args:
            routes: List of enriched routes with names/descriptions
            origin_addr: Origin address for display
            dest_addr: Destination address for display
            
        Returns:
            Complete HTML string
        """
        # Calculate map bounds
        bounds = self._calculate_bounds(routes)
        
        # Generate map configuration
        map_config = self._create_map_config(routes, bounds)
        
        # Generate route cards HTML
        route_cards = self._generate_route_cards(routes)
        
        # Render template
        html = self.template.format(
            title=f"Routes: {origin_addr} to {dest_addr}",
            origin_addr=origin_addr,
            dest_addr=dest_addr,
            map_config=json.dumps(map_config),
            route_cards=route_cards,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Inline assets for portability
        html = self._inline_assets(html)
        
        return html
    
    def _create_map_config(self, routes: List[EnrichedRoute], bounds: dict) -> dict:
        """Create map configuration object"""
        return {
            'bounds': bounds,
            'routes': [
                {
                    'id': route.route_id,
                    'name': route.name,
                    'color': route.color,
                    'geometry': [{'lat': c.lat, 'lng': c.lon} for c in route.geometry]
                }
                for route in routes
            ],
            'origin': {'lat': routes[0].geometry[0].lat, 'lng': routes[0].geometry[0].lon},
            'destination': {'lat': routes[0].geometry[-1].lat, 'lng': routes[0].geometry[-1].lon}
        }
    
    def _generate_route_cards(self, routes: List[EnrichedRoute]) -> str:
        """Generate HTML for route information cards"""
        cards_html = []
        
        for i, route in enumerate(routes, 1):
            card_html = f"""
            <div class="route-card" data-route-id="{route.route_id}">
                <div class="route-header">
                    <span class="route-number" style="background-color: {route.color};">{i}</span>
                    <h3 class="route-name">{route.name}</h3>
                </div>
                <div class="route-stats">
                    <span class="distance">{route.distance_km} km</span>
                    <span class="duration">{route.duration_formatted}</span>
                </div>
                <p class="route-description">{route.description}</p>
                {self._generate_roads_list(route.major_roads)}
            </div>
            """
            cards_html.append(card_html)
        
        return '\n'.join(cards_html)
    
    def _generate_roads_list(self, roads: List[str]) -> str:
        """Generate HTML for major roads list"""
        if not roads:
            return ""
        
        roads_html = '<div class="major-roads"><strong>Via:</strong> '
        roads_html += ', '.join(roads[:3])  # Show top 3 roads
        if len(roads) > 3:
            roads_html += f' and {len(roads) - 3} more'
        roads_html += '</div>'
        
        return roads_html
    
    def _calculate_bounds(self, routes: List[EnrichedRoute]) -> dict:
        """Calculate bounding box for all routes"""
        all_coords = []
        for route in routes:
            all_coords.extend(route.geometry)
        
        lats = [c.lat for c in all_coords]
        lons = [c.lon for c in all_coords]
        
        return {
            'southwest': {'lat': min(lats), 'lng': min(lons)},
            'northeast': {'lat': max(lats), 'lng': max(lons)}
        }
    
    def _inline_assets(self, html: str) -> str:
        """Inline CSS and JavaScript assets for portability"""
        # Load and inline Leaflet CSS/JS
        # Load and inline custom styles
        # Implementation details...
        return html
    
    def _load_template(self) -> str:
        """Load HTML template from file"""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Return default template if file not found
            return self._get_default_template()
    
    def _get_default_template(self) -> str:
        """Return default HTML template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* CSS styles will be inlined here */
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Route Options</h1>
            <p class="route-summary">{origin_addr} → {dest_addr}</p>
        </header>
        
        <div id="map" style="height: 400px; width: 100%;"></div>
        
        <div class="routes-container">
            {route_cards}
        </div>
        
        <footer>
            <p class="timestamp">Generated: {timestamp}</p>
        </footer>
    </div>
    
    <script>
        // Leaflet.js and map initialization will be inlined here
        const mapConfig = {map_config};
        // Map initialization code...
    </script>
</body>
</html>
        """
```

## 🔄 Error Handling

### Standard Error Response Format

```python
@dataclass
class ErrorResponse:
    error_code: str
    message: str
    details: Optional[dict] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> dict:
        return {
            'error': {
                'code': self.error_code,
                'message': self.message,
                'details': self.details,
                'timestamp': self.timestamp
            }
        }

# Error Codes
class ErrorCodes:
    GEOCODING_FAILED = "GEOCODING_FAILED"
    ROUTING_FAILED = "ROUTING_FAILED"
    LLM_FAILED = "LLM_FAILED"
    INVALID_CONFIG = "INVALID_CONFIG"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
```

## 📊 Response Formats

### Successful Route Generation Response

```json
{
    "success": true,
    "data": {
        "origin": {
            "address": "123 Main St, Springfield, IL",
            "coordinates": {"lat": 39.7817, "lon": -89.6501}
        },
        "destination": {
            "address": "456 Oak Ave, Shelbyville, IL", 
            "coordinates": {"lat": 39.4042, "lon": -88.7906}
        },
        "routes": [
            {
                "id": "route_0",
                "name": "Highway Express",
                "description": "Fast 45-minute drive via I-72, minimal stops with highway speeds.",
                "distance_km": 42.3,
                "duration_formatted": "45m",
                "color": "#e74c3c",
                "major_roads": ["Interstate 72", "IL-4", "Main Street"],
                "geometry": [
                    {"lat": 39.7817, "lon": -89.6501},
                    {"lat": 39.7820, "lon": -89.6480},
                    "..."
                ]
            }
        ],
        "generated_at": "2024-01-15T10:30:00Z",
        "processing_time_ms": 3247
    }
}
```

### Error Response Examples

```json
{
    "success": false,
    "error": {
        "code": "GEOCODING_FAILED",
        "message": "Could not find coordinates for address",
        "details": {
            "address": "Invalid Address 123",
            "service": "nominatim"
        },
        "timestamp": "2024-01-15T10:30:00Z"
    }
}
```

## 🧪 Testing Interfaces

### Mock Data Providers

```python
class MockOSRMService(OSRMService):
    """Mock OSRM service for testing"""
    
    def __init__(self, mock_routes: List[Route]):
        self.mock_routes = mock_routes
    
    async def get_routes(self, origin: Coordinates, destination: Coordinates, 
                        alternatives: bool = True, max_alternatives: int = 3) -> List[Route]:
        return self.mock_routes[:max_alternatives]

class MockLLMService(LLMService):
    """Mock LLM service for testing"""
    
    async def generate_route_descriptions(self, routes: List[Route]) -> List[Tuple[str, str]]:
        descriptions = []
        for i, route in enumerate(routes, 1):
            name = f"Test Route {i}"
            desc = f"Test description for route {i} ({route.distance_km} km)"
            descriptions.append((name, desc))
        return descriptions
```

This comprehensive API specification provides the foundation for implementing the LLM-Powered Route Planner with clear interfaces, data models, and error handling patterns.