import asyncio
from typing import Any, Dict, Optional

import pytest
import polyline as polyline_lib

from pathypotomus.models.coordinates import Coordinates
from pathypotomus.models.route import Route


# --- Test doubles for aiohttp-like session/response ---
class _FakeResponse:
    def __init__(self, status: int, json_data: Dict[str, Any]):
        self.status = status
        self._json_data = json_data

    async def json(self) -> Dict[str, Any]:
        return self._json_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeSession:
    def __init__(self, status: int, json_data: Dict[str, Any]):
        self._status = status
        self._json_data = json_data
        self.last_url: Optional[str] = None
        self.last_params: Optional[Dict[str, Any]] = None

    def get(self, url: str, params: Optional[Dict[str, Any]] = None):
        self.last_url = url
        self.last_params = params or {}
        return _FakeResponse(self._status, self._json_data)


# --- Fixtures ---
@pytest.fixture
def origin_coords() -> Coordinates:
    return Coordinates(latitude=41.8781, longitude=-87.6298)


@pytest.fixture
def dest_coords() -> Coordinates:
    return Coordinates(latitude=43.0389, longitude=-87.9065)


def _make_osrm_route(geometry_points, distance: float, duration: float, step_names):
    encoded = polyline_lib.encode([(p.latitude, p.longitude) for p in geometry_points])
    legs = [
        {
            "steps": [
                {"name": name} for name in step_names
            ]
        }
    ]
    return {
        "geometry": encoded,
        "distance": distance,
        "duration": duration,
        "legs": legs,
    }


def _make_osrm_ok_response(routes: list[dict]) -> Dict[str, Any]:
    return {
        "code": "Ok",
        "routes": routes,
    }


def _make_osrm_error_response(message: str) -> Dict[str, Any]:
    return {
        "code": "Error",
        "message": message,
    }


@pytest.mark.asyncio
async def test_get_routes_parses_response_into_route_models(origin_coords, dest_coords):
    # Two simple routes with distinct roads
    geom1 = [origin_coords, Coordinates(latitude=42.0, longitude=-87.7), dest_coords]
    geom2 = [origin_coords, Coordinates(latitude=41.95, longitude=-87.75), dest_coords]

    osrm_routes = [
        _make_osrm_route(geom1, distance=150000.0, duration=5400.0, step_names=["I-94 N", "Lake Shore Drive", "Main St"]),
        _make_osrm_route(geom2, distance=160000.0, duration=5600.0, step_names=["US-41", "I-94 N"]),
    ]

    fake_session = _FakeSession(status=200, json_data=_make_osrm_ok_response(osrm_routes))

    # Import here to avoid circular during collection; service doesn't exist yet in TDD
    from pathypotomus.services.osrm import OSRMService

    service = OSRMService(base_url="https://router.project-osrm.org", session=fake_session)

    routes = await service.get_routes(origin_coords, dest_coords, alternatives=True, max_alternatives=3)

    assert isinstance(routes, list)
    assert len(routes) == 2
    assert all(isinstance(r, Route) for r in routes)

    r1, r2 = routes
    # Geometry decoded
    assert r1.geometry[0] == origin_coords
    assert r1.geometry[-1] == dest_coords
    # Distance/duration propagated
    assert r1.distance == pytest.approx(150000.0)
    assert r1.duration == pytest.approx(5400.0)
    # Summary and major roads extracted
    assert "via" in r1.summary or r1.summary == "Local roads"
    assert len(r1.major_roads) >= 1

    # Verify URL and params used
    assert fake_session.last_url.startswith("https://router.project-osrm.org/route/v1/driving/")
    assert fake_session.last_params["alternatives"] == "true"
    assert fake_session.last_params["overview"] == "simplified"
    assert fake_session.last_params["steps"] == "true"
    assert fake_session.last_params["geometries"] == "polyline"


@pytest.mark.asyncio
async def test_get_routes_respects_max_alternatives(origin_coords, dest_coords):
    geom = [origin_coords, dest_coords]
    osrm_routes = [
        _make_osrm_route(geom, 1000.0 + i * 10.0, 100.0 + i * 5.0, [f"Road {i}"]) for i in range(5)
    ]

    fake_session = _FakeSession(status=200, json_data=_make_osrm_ok_response(osrm_routes))
    from pathypotomus.services.osrm import OSRMService

    service = OSRMService(session=fake_session)
    routes = await service.get_routes(origin_coords, dest_coords, alternatives=True, max_alternatives=2)

    assert len(routes) == 2


@pytest.mark.asyncio
async def test_get_routes_raises_on_http_error(origin_coords, dest_coords):
    fake_session = _FakeSession(status=503, json_data={})
    from pathypotomus.services.osrm import OSRMService, RoutingError

    service = OSRMService(session=fake_session)

    with pytest.raises(RoutingError):
        await service.get_routes(origin_coords, dest_coords)


@pytest.mark.asyncio
async def test_get_routes_raises_on_osrm_error_code(origin_coords, dest_coords):
    fake_session = _FakeSession(status=200, json_data=_make_osrm_error_response("NoRoute"))
    from pathypotomus.services.osrm import OSRMService, RoutingError

    service = OSRMService(session=fake_session)

    with pytest.raises(RoutingError):
        await service.get_routes(origin_coords, dest_coords)