"""Tests for coordinates model."""
import pytest
from pydantic import ValidationError

from pathypotomus.models.coordinates import Coordinates


class TestCoordinates:
    """Test coordinates model validation and functionality."""

    def test_valid_coordinates(self):
        """Test valid coordinates creation."""
        coords = Coordinates(latitude=41.8781, longitude=-87.6298)
        
        assert coords.latitude == 41.8781
        assert coords.longitude == -87.6298

    def test_coordinates_from_tuple(self):
        """Test creating coordinates from tuple."""
        coords = Coordinates.from_tuple((41.8781, -87.6298))
        
        assert coords.latitude == 41.8781
        assert coords.longitude == -87.6298

    def test_coordinates_to_tuple(self):
        """Test converting coordinates to tuple."""
        coords = Coordinates(latitude=41.8781, longitude=-87.6298)
        
        assert coords.to_tuple() == (41.8781, -87.6298)

    def test_invalid_latitude_too_high(self):
        """Test validation error for latitude > 90."""
        with pytest.raises(ValidationError) as exc_info:
            Coordinates(latitude=91.0, longitude=0.0)
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'latitude' for error in errors)

    def test_invalid_latitude_too_low(self):
        """Test validation error for latitude < -90."""
        with pytest.raises(ValidationError) as exc_info:
            Coordinates(latitude=-91.0, longitude=0.0)
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'latitude' for error in errors)

    def test_invalid_longitude_too_high(self):
        """Test validation error for longitude > 180."""
        with pytest.raises(ValidationError) as exc_info:
            Coordinates(latitude=0.0, longitude=181.0)
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'longitude' for error in errors)

    def test_invalid_longitude_too_low(self):
        """Test validation error for longitude < -180."""
        with pytest.raises(ValidationError) as exc_info:
            Coordinates(latitude=0.0, longitude=-181.0)
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'longitude' for error in errors)

    def test_distance_calculation(self):
        """Test distance calculation between two coordinates."""
        chicago = Coordinates(latitude=41.8781, longitude=-87.6298)
        milwaukee = Coordinates(latitude=43.0389, longitude=-87.9065)
        
        distance = chicago.distance_to(milwaukee)
        
        # Distance between Chicago and Milwaukee is approximately 130 km
        assert 120 < distance < 140

    def test_distance_to_same_point(self):
        """Test distance calculation to same point."""
        coords = Coordinates(latitude=41.8781, longitude=-87.6298)
        
        distance = coords.distance_to(coords)
        
        assert distance == 0.0

    def test_string_representation(self):
        """Test string representation of coordinates."""
        coords = Coordinates(latitude=41.8781, longitude=-87.6298)
        
        str_repr = str(coords)
        
        assert "41.8781" in str_repr
        assert "-87.6298" in str_repr

    def test_equality(self):
        """Test coordinates equality comparison."""
        coords1 = Coordinates(latitude=41.8781, longitude=-87.6298)
        coords2 = Coordinates(latitude=41.8781, longitude=-87.6298)
        coords3 = Coordinates(latitude=42.0, longitude=-87.0)
        
        assert coords1 == coords2
        assert coords1 != coords3

    def test_hashable(self):
        """Test that coordinates are hashable."""
        coords1 = Coordinates(latitude=41.8781, longitude=-87.6298)
        coords2 = Coordinates(latitude=41.8781, longitude=-87.6298)
        
        # Should be able to use as dict keys
        coord_dict = {coords1: "Chicago"}
        assert coord_dict[coords2] == "Chicago"

    def test_coordinates_precision(self):
        """Test coordinates with high precision."""
        coords = Coordinates(latitude=41.87812345, longitude=-87.62984567)
        
        assert coords.latitude == 41.87812345
        assert coords.longitude == -87.62984567