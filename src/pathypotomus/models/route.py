"""Route model for representing navigation routes."""
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from .coordinates import Coordinates


class Route(BaseModel):
    """
    Represents a navigation route with geometry, distance, duration, and metadata.
    
    Contains the route path as a series of coordinates, along with computed
    metrics and optional AI-generated descriptions.
    """
    
    geometry: List[Coordinates] = Field(
        ...,
        min_length=2,
        description="List of coordinates defining the route path"
    )
    distance: float = Field(
        ...,
        ge=0.0,
        description="Route distance in meters"
    )
    duration: float = Field(
        ...,
        ge=0.0,
        description="Estimated travel time in seconds"
    )
    summary: str = Field(
        default="",
        description="Brief route summary (e.g., 'via Highway 1')"
    )
    major_roads: List[str] = Field(
        default_factory=list,
        description="List of major roads used in this route"
    )
    name: Optional[str] = Field(
        default=None,
        description="AI-generated route name"
    )
    description: Optional[str] = Field(
        default=None,
        description="AI-generated route description"
    )
    
    @field_validator('geometry')
    @classmethod
    def validate_geometry(cls, v: List[Coordinates]) -> List[Coordinates]:
        """Validate that geometry has at least 2 points."""
        if len(v) < 2:
            raise ValueError("Route geometry must contain at least 2 coordinate points")
        return v
    
    @property
    def start_point(self) -> Coordinates:
        """Get the starting point of the route."""
        return self.geometry[0]
    
    @property
    def end_point(self) -> Coordinates:
        """Get the ending point of the route."""
        return self.geometry[-1]
    
    @property
    def distance_formatted(self) -> str:
        """
        Get formatted distance string.
        
        Returns distance in kilometers if >= 1000m, otherwise in meters.
        
        Returns:
            str: Formatted distance (e.g., "5.2 km" or "850 m")
        """
        if self.distance >= 1000.0:
            km = self.distance / 1000.0
            return f"{km:.1f} km"
        else:
            return f"{int(round(self.distance))} m"
    
    @property
    def duration_formatted(self) -> str:
        """
        Get formatted duration string.
        
        Returns duration in hours and minutes, minutes only, or seconds only
        depending on the total duration.
        
        Returns:
            str: Formatted duration (e.g., "1h 25m", "15m", or "45s")
        """
        total_seconds = int(round(self.duration))
        
        if total_seconds >= 3600:  # 1 hour or more
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        elif total_seconds >= 60:  # 1 minute or more
            minutes = total_seconds // 60
            return f"{minutes}m"
        else:  # Less than 1 minute
            return f"{total_seconds}s"
    
    def __str__(self) -> str:
        """String representation of the route."""
        parts = [
            f"Route: {self.distance_formatted}",
            f"{self.duration_formatted}"
        ]
        
        if self.name:
            parts.insert(0, f"'{self.name}'")
        elif self.summary:
            parts.append(f"({self.summary})")
        
        return " ".join(parts)
    
    def __repr__(self) -> str:
        """Detailed string representation of the route."""
        return (f"Route(distance={self.distance}m, duration={self.duration}s, "
                f"points={len(self.geometry)}, summary='{self.summary}')")
    
    def __eq__(self, other) -> bool:
        """Check equality with another Route object."""
        if not isinstance(other, Route):
            return False
        return (
            self.geometry == other.geometry and
            self.distance == other.distance and
            self.duration == other.duration and
            self.summary == other.summary and
            self.major_roads == other.major_roads
        )