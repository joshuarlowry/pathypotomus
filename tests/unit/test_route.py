"""Tests for route model."""
from typing import List
import pytest
from pydantic import ValidationError

from pathypotomus.models.coordinates import Coordinates
from pathypotomus.models.route import Route


class TestRoute:
    """Test route model validation and functionality."""

    def test_valid_route(self):
        """Test valid route creation."""
        geometry = [
            Coordinates(latitude=41.8781, longitude=-87.6298),
            Coordinates(latitude=41.8800, longitude=-87.6300),
            Coordinates(latitude=41.8850, longitude=-87.6350)
        ]
        
        route = Route(
            geometry=geometry,
            distance=5000.0,
            duration=600.0,
            summary="via Lake Shore Drive",
            major_roads=["Lake Shore Drive", "Michigan Avenue"]
        )
        
        assert len(route.geometry) == 3
        assert route.distance == 5000.0
        assert route.duration == 600.0
        assert route.summary == "via Lake Shore Drive"
        assert route.major_roads == ["Lake Shore Drive", "Michigan Avenue"]

    def test_route_with_minimal_data(self):
        """Test route creation with minimal required data."""
        geometry = [
            Coordinates(latitude=41.8781, longitude=-87.6298),
            Coordinates(latitude=41.8850, longitude=-87.6350)
        ]
        
        route = Route(
            geometry=geometry,
            distance=3000.0,
            duration=300.0
        )
        
        assert len(route.geometry) == 2
        assert route.distance == 3000.0
        assert route.duration == 300.0
        assert route.summary == ""
        assert route.major_roads == []
        assert route.name is None
        assert route.description is None

    def test_invalid_empty_geometry(self):
        """Test validation error for empty geometry."""
        with pytest.raises(ValidationError) as exc_info:
            Route(
                geometry=[],
                distance=1000.0,
                duration=100.0
            )
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'geometry' for error in errors)

    def test_invalid_single_point_geometry(self):
        """Test validation error for single point geometry."""
        with pytest.raises(ValidationError) as exc_info:
            Route(
                geometry=[Coordinates(latitude=41.8781, longitude=-87.6298)],
                distance=1000.0,
                duration=100.0
            )
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'geometry' for error in errors)

    def test_invalid_negative_distance(self):
        """Test validation error for negative distance."""
        geometry = [
            Coordinates(latitude=41.8781, longitude=-87.6298),
            Coordinates(latitude=41.8850, longitude=-87.6350)
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            Route(
                geometry=geometry,
                distance=-1000.0,
                duration=100.0
            )
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'distance' for error in errors)

    def test_invalid_negative_duration(self):
        """Test validation error for negative duration."""
        geometry = [
            Coordinates(latitude=41.8781, longitude=-87.6298),
            Coordinates(latitude=41.8850, longitude=-87.6350)
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            Route(
                geometry=geometry,
                distance=1000.0,
                duration=-100.0
            )
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'duration' for error in errors)

    def test_route_start_point(self):
        """Test getting the start point of a route."""
        geometry = [
            Coordinates(latitude=41.8781, longitude=-87.6298),
            Coordinates(latitude=41.8800, longitude=-87.6300),
            Coordinates(latitude=41.8850, longitude=-87.6350)
        ]
        
        route = Route(
            geometry=geometry,
            distance=5000.0,
            duration=600.0
        )
        
        start = route.start_point
        assert start.latitude == 41.8781
        assert start.longitude == -87.6298

    def test_route_end_point(self):
        """Test getting the end point of a route."""
        geometry = [
            Coordinates(latitude=41.8781, longitude=-87.6298),
            Coordinates(latitude=41.8800, longitude=-87.6300),
            Coordinates(latitude=41.8850, longitude=-87.6350)
        ]
        
        route = Route(
            geometry=geometry,
            distance=5000.0,
            duration=600.0
        )
        
        end = route.end_point
        assert end.latitude == 41.8850
        assert end.longitude == -87.6350

    def test_route_distance_formatted(self):
        """Test formatted distance display."""
        geometry = [
            Coordinates(latitude=41.8781, longitude=-87.6298),
            Coordinates(latitude=41.8850, longitude=-87.6350)
        ]
        
        # Test kilometers
        route_km = Route(
            geometry=geometry,
            distance=5432.1,
            duration=600.0
        )
        assert route_km.distance_formatted == "5.4 km"
        
        # Test meters
        route_m = Route(
            geometry=geometry,
            distance=876.5,
            duration=60.0
        )
        assert route_m.distance_formatted == "876 m"

    def test_route_duration_formatted(self):
        """Test formatted duration display."""
        geometry = [
            Coordinates(latitude=41.8781, longitude=-87.6298),
            Coordinates(latitude=41.8850, longitude=-87.6350)
        ]
        
        # Test hours and minutes
        route_long = Route(
            geometry=geometry,
            distance=50000.0,
            duration=4567.0  # 76 minutes, 7 seconds
        )
        assert route_long.duration_formatted == "1h 16m"
        
        # Test minutes only
        route_medium = Route(
            geometry=geometry,
            distance=5000.0,
            duration=567.0  # 9 minutes, 27 seconds
        )
        assert route_medium.duration_formatted == "9m"
        
        # Test seconds only
        route_short = Route(
            geometry=geometry,
            distance=500.0,
            duration=45.0
        )
        assert route_short.duration_formatted == "45s"

    def test_route_with_ai_generated_content(self):
        """Test route with AI-generated name and description."""
        geometry = [
            Coordinates(latitude=41.8781, longitude=-87.6298),
            Coordinates(latitude=41.8850, longitude=-87.6350)
        ]
        
        route = Route(
            geometry=geometry,
            distance=5000.0,
            duration=600.0,
            name="Lakefront Express",
            description="Scenic route along Chicago's beautiful lakefront with minimal traffic."
        )
        
        assert route.name == "Lakefront Express"
        assert route.description == "Scenic route along Chicago's beautiful lakefront with minimal traffic."

    def test_route_equality(self):
        """Test route equality comparison."""
        geometry1 = [
            Coordinates(latitude=41.8781, longitude=-87.6298),
            Coordinates(latitude=41.8850, longitude=-87.6350)
        ]
        geometry2 = [
            Coordinates(latitude=41.8781, longitude=-87.6298),
            Coordinates(latitude=41.8850, longitude=-87.6350)
        ]
        geometry3 = [
            Coordinates(latitude=42.0, longitude=-87.0),
            Coordinates(latitude=42.1, longitude=-87.1)
        ]
        
        route1 = Route(geometry=geometry1, distance=5000.0, duration=600.0)
        route2 = Route(geometry=geometry2, distance=5000.0, duration=600.0)
        route3 = Route(geometry=geometry3, distance=5000.0, duration=600.0)
        
        assert route1 == route2
        assert route1 != route3

    def test_route_string_representation(self):
        """Test string representation of route."""
        geometry = [
            Coordinates(latitude=41.8781, longitude=-87.6298),
            Coordinates(latitude=41.8850, longitude=-87.6350)
        ]
        
        route = Route(
            geometry=geometry,
            distance=5000.0,
            duration=600.0,
            summary="via Main Street"
        )
        
        str_repr = str(route)
        assert "5.0 km" in str_repr
        assert "10m" in str_repr
        assert "Main Street" in str_repr