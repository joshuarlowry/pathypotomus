"""Coordinates model for geographical locations."""
import math
from typing import Tuple

from pydantic import BaseModel, Field, field_validator


class Coordinates(BaseModel):
    """
    Represents geographical coordinates with latitude and longitude.
    
    Provides validation for coordinate ranges and distance calculations.
    """
    
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude in decimal degrees (-90 to 90)"
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude in decimal degrees (-180 to 180)"
    )
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        """Validate latitude is within valid range."""
        if not -90.0 <= v <= 90.0:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        """Validate longitude is within valid range."""
        if not -180.0 <= v <= 180.0:
            raise ValueError("Longitude must be between -180 and 180 degrees")
        return v
    
    @classmethod
    def from_tuple(cls, coord_tuple: Tuple[float, float]) -> 'Coordinates':
        """
        Create Coordinates from a tuple of (latitude, longitude).
        
        Args:
            coord_tuple: Tuple containing (latitude, longitude)
            
        Returns:
            Coordinates: New coordinates instance
        """
        return cls(latitude=coord_tuple[0], longitude=coord_tuple[1])
    
    def to_tuple(self) -> Tuple[float, float]:
        """
        Convert coordinates to a tuple of (latitude, longitude).
        
        Returns:
            Tuple[float, float]: (latitude, longitude)
        """
        return (self.latitude, self.longitude)
    
    def distance_to(self, other: 'Coordinates') -> float:
        """
        Calculate the great circle distance to another coordinate point.
        
        Uses the Haversine formula to calculate the distance between two points
        on the Earth's surface specified by latitude and longitude.
        
        Args:
            other: The other coordinate point
            
        Returns:
            float: Distance in kilometers
        """
        if self == other:
            return 0.0
        
        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(self.latitude)
        lon1_rad = math.radians(self.longitude)
        lat2_rad = math.radians(other.latitude)
        lon2_rad = math.radians(other.longitude)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        earth_radius_km = 6371.0
        
        return earth_radius_km * c
    
    def __str__(self) -> str:
        """String representation of coordinates."""
        return f"Coordinates(lat={self.latitude}, lon={self.longitude})"
    
    def __repr__(self) -> str:
        """Detailed string representation of coordinates."""
        return f"Coordinates(latitude={self.latitude}, longitude={self.longitude})"
    
    def __hash__(self) -> int:
        """Make coordinates hashable for use in sets and as dict keys."""
        return hash((self.latitude, self.longitude))
    
    def __eq__(self, other) -> bool:
        """Check equality with another Coordinates object."""
        if not isinstance(other, Coordinates):
            return False
        return (self.latitude == other.latitude and 
                self.longitude == other.longitude)