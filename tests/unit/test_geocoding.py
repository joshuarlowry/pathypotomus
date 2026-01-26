import pytest
from unittest.mock import MagicMock, patch
from geopy.exc import GeocoderTimedOut

from pathypotomus.services.geocoding import GeocodingService, GeocodingError
from pathypotomus.models.coordinates import Coordinates

def test_geocode_success():
    with patch('pathypotomus.services.geocoding.Nominatim') as mock_nominatim_cls:
        mock_geolocator = MagicMock()
        mock_nominatim_cls.return_value = mock_geolocator
        
        mock_location = MagicMock()
        mock_location.latitude = 40.7128
        mock_location.longitude = -74.0060
        mock_geolocator.geocode.return_value = mock_location
        
        service = GeocodingService()
        result = service.geocode("New York, NY")
        
        assert isinstance(result, Coordinates)
        assert result.latitude == 40.7128
        assert result.longitude == -74.0060
        mock_geolocator.geocode.assert_called_with("New York, NY")

def test_geocode_not_found():
    with patch('pathypotomus.services.geocoding.Nominatim') as mock_nominatim_cls:
        mock_geolocator = MagicMock()
        mock_nominatim_cls.return_value = mock_geolocator
        mock_geolocator.geocode.return_value = None
        
        service = GeocodingService()
        
        with pytest.raises(GeocodingError, match="Could not find coordinates"):
            service.geocode("Nonexistent Place")

def test_geocode_service_error():
    with patch('pathypotomus.services.geocoding.Nominatim') as mock_nominatim_cls:
        mock_geolocator = MagicMock()
        mock_nominatim_cls.return_value = mock_geolocator
        mock_geolocator.geocode.side_effect = GeocoderTimedOut()
        
        service = GeocodingService()
        
        with pytest.raises(GeocodingError, match="Geocoding service unavailable"):
            service.geocode("London")
