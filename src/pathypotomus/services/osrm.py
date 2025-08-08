from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import polyline

from pathypotomus.models.coordinates import Coordinates
from pathypotomus.models.route import Route

try:
    import aiohttp  # type: ignore
except Exception:  # pragma: no cover - aiohttp not required for unit tests
    aiohttp = None  # type: ignore


class RoutingError(Exception):
    """Raised when routing operations fail"""


@dataclass
class _HttpClient:
    """Lightweight wrapper to abstract an aiohttp-like client session."""

    session: any

    async def get_json(self, url: str, params: dict) -> tuple[int, dict]:
        async with self.session.get(url, params=params) as response:
            return response.status, await response.json()


class OSRMService:
    """OSRM routing service client."""

    def __init__(
        self,
        base_url: str = "https://router.project-osrm.org",
        session: Optional[any] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session

    async def get_routes(
        self,
        origin: Coordinates,
        destination: Coordinates,
        alternatives: bool = True,
        max_alternatives: int = 3,
    ) -> List[Route]:
        """Get route alternatives from OSRM and parse into Route models."""
        url = self._build_route_url(origin, destination)
        params = {
            "alternatives": "true" if alternatives else "false",
            "overview": "simplified",
            "steps": "true",
            "geometries": "polyline",
        }

        # Choose or create a session
        client: _HttpClient
        if self.session is not None:
            client = _HttpClient(self.session)
        else:
            if aiohttp is None:
                raise RoutingError("aiohttp is required for network calls but is not available")
            session = aiohttp.ClientSession()
            client = _HttpClient(session)  # pragma: no cover - not used in unit tests

        status, data = await client.get_json(url, params=params)
        if status != 200:
            raise RoutingError(f"OSRM request failed: HTTP {status}")

        if data.get("code") != "Ok":
            raise RoutingError(f"OSRM error: {data.get('message', 'Unknown error')}")

        osrm_routes = data.get("routes", [])[:max_alternatives]
        parsed: List[Route] = []
        for idx, osrm_route in enumerate(osrm_routes):
            parsed.append(self._parse_osrm_route(osrm_route))
        return parsed

    def _build_route_url(self, origin: Coordinates, destination: Coordinates) -> str:
        coords = f"{origin.longitude},{origin.latitude};{destination.longitude},{destination.latitude}"
        return f"{self.base_url}/route/v1/driving/{coords}"

    def _parse_osrm_route(self, osrm_route: dict) -> Route:
        geometry = self._decode_polyline(osrm_route["geometry"])
        major_roads = self._extract_major_roads(osrm_route.get("legs", []))
        summary = self._generate_summary(major_roads)
        return Route(
            geometry=geometry,
            distance=float(osrm_route["distance"]),
            duration=float(osrm_route["duration"]),
            summary=summary,
            major_roads=major_roads,
        )

    def _decode_polyline(self, encoded: str) -> List[Coordinates]:
        points = polyline.decode(encoded)
        return [Coordinates(latitude=lat, longitude=lon) for lat, lon in points]

    def _extract_major_roads(self, legs: List[dict]) -> List[str]:
        roads: list[str] = []
        for leg in legs:
            for step in leg.get("steps", []):
                name = (step.get("name") or "").strip()
                if name and len(name) > 1 and name not in roads:
                    roads.append(name)
        return roads[:5]

    def _generate_summary(self, major_roads: List[str]) -> str:
        if not major_roads:
            return "Local roads"
        if len(major_roads) == 1:
            return f"via {major_roads[0]}"
        return f"via {major_roads[0]} and {len(major_roads) - 1} other roads"