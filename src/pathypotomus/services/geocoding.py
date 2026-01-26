"""Geocoding service for converting addresses to coordinates."""
import logging
from typing import Optional

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

from pathypotomus.models.coordinates import Coordinates

logger = logging.getLogger(__name__)


class GeocodingError(Exception):
    """Raised when geocoding fails."""


class GeocodingService:
    """Service for geocoding addresses using Nominatim (OSM)."""

    def __init__(self, user_agent: str = "pathypotomus/1.0"):
        """
        Initialize the geocoding service.

        Args:
            user_agent: User agent string for Nominatim service
        """
        self.geolocator = Nominatim(user_agent=user_agent)

    def geocode(self, address: str) -> Coordinates:
        """
        Convert an address string to coordinates.

        Args:
            address: The address string to geocode

        Returns:
            Coordinates: The corresponding coordinates

        Raises:
            GeocodingError: If the address cannot be found or service is unavailable
        """
        try:
            logger.info(f"Geocoding address: {address}")
            location = self.geolocator.geocode(address)

            if location is None:
                raise GeocodingError(f"Could not find coordinates for address: {address}")

            return Coordinates(
                latitude=location.latitude,
                longitude=location.longitude
            )

        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            raise GeocodingError(f"Geocoding service unavailable: {e}")
        except Exception as e:
            if isinstance(e, GeocodingError):
                raise
            raise GeocodingError(f"Unexpected error during geocoding: {e}")
