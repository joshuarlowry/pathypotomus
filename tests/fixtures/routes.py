"""Test fixtures for route data."""
import pytest
from pathypotomus.models.coordinates import Coordinates
from pathypotomus.models.route import Route


@pytest.fixture
def chicago_coordinates():
    """Chicago downtown coordinates."""
    return Coordinates(latitude=41.8781, longitude=-87.6298)


@pytest.fixture
def milwaukee_coordinates():
    """Milwaukee downtown coordinates."""
    return Coordinates(latitude=43.0389, longitude=-87.9065)


@pytest.fixture
def sample_route_geometry():
    """Sample route geometry with multiple points."""
    return [
        Coordinates(latitude=41.8781, longitude=-87.6298),  # Chicago
        Coordinates(latitude=41.8800, longitude=-87.6300),
        Coordinates(latitude=41.8850, longitude=-87.6350),
        Coordinates(latitude=42.0000, longitude=-87.7000),
        Coordinates(latitude=43.0389, longitude=-87.9065),  # Milwaukee
    ]


@pytest.fixture
def sample_route(sample_route_geometry):
    """Sample route with basic data."""
    return Route(
        geometry=sample_route_geometry,
        distance=150000.0,  # 150 km
        duration=5400.0,    # 90 minutes
        summary="via I-94 N",
        major_roads=["I-94 North", "Lake Shore Drive"]
    )


@pytest.fixture
def sample_route_with_ai_content(sample_route_geometry):
    """Sample route with AI-generated content."""
    return Route(
        geometry=sample_route_geometry,
        distance=150000.0,
        duration=5400.0,
        summary="via I-94 N",
        major_roads=["I-94 North", "Lake Shore Drive"],
        name="Interstate Express",
        description="Fast highway route through scenic Wisconsin countryside with minimal traffic delays."
    )


@pytest.fixture
def short_route():
    """Short route for testing formatting."""
    return Route(
        geometry=[
            Coordinates(latitude=41.8781, longitude=-87.6298),
            Coordinates(latitude=41.8785, longitude=-87.6302)
        ],
        distance=500.0,  # 500 meters
        duration=120.0,  # 2 minutes
        summary="via Main St"
    )


@pytest.fixture
def multiple_routes(sample_route, short_route):
    """Multiple routes for testing collections."""
    long_route = Route(
        geometry=[
            Coordinates(latitude=41.8781, longitude=-87.6298),
            Coordinates(latitude=42.3601, longitude=-71.0589)  # Boston
        ],
        distance=1500000.0,  # 1500 km
        duration=54000.0,    # 15 hours
        summary="via I-90 E",
        major_roads=["I-90 East", "Mass Pike"]
    )
    
    return [sample_route, short_route, long_route]


@pytest.fixture
def chicago_to_milwaukee_addresses():
    """Sample addresses for testing geocoding."""
    return {
        'origin': '123 N Michigan Ave, Chicago, IL',
        'destination': '456 E Wisconsin Ave, Milwaukee, WI'
    }