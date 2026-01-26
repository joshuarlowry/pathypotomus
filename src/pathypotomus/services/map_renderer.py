"""Service for rendering routes on a map."""
import logging
from typing import List
from pathlib import Path

import folium

from pathypotomus.models.coordinates import Coordinates
from pathypotomus.models.route import Route

logger = logging.getLogger(__name__)


class MapRenderer:
    """Service for rendering routes on a folium map."""

    def __init__(self):
        """Initialize the map renderer."""
        pass

    def render(
        self,
        origin: Coordinates,
        destination: Coordinates,
        routes: List[Route],
        output_path: str,
        title: str = "Route Options"
    ) -> str:
        """
        Render routes to an HTML file.

        Args:
            origin: Origin coordinates
            destination: Destination coordinates
            routes: List of routes to display
            output_path: Path to save the HTML file
            title: Title for the map page

        Returns:
            str: Absolute path to the generated HTML file
        """
        if not routes:
            logger.warning("No routes to render")
            return ""

        # Calculate center of map
        center_lat = (origin.latitude + destination.latitude) / 2
        center_lon = (origin.longitude + destination.longitude) / 2

        # Create map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11)

        # Add title (hacky way via HTML injection into element or just standard popup)
        # For simplicity, we'll just add markers and lines.

        # Add Origin and Destination Markers
        folium.Marker(
            [origin.latitude, origin.longitude],
            popup="Origin",
            icon=folium.Icon(color="green", icon="play")
        ).add_to(m)

        folium.Marker(
            [destination.latitude, destination.longitude],
            popup="Destination",
            icon=folium.Icon(color="red", icon="stop")
        ).add_to(m)

        # Colors for different routes
        colors = ["blue", "orange", "purple", "darkgreen", "darkblue", "cadetblue"]

        for idx, route in enumerate(routes):
            color = colors[idx % len(colors)]
            
            # Prepare route line
            points = [(p.latitude, p.longitude) for p in route.geometry]
            
            # Prepare popup content
            name = route.name or f"Route {idx + 1}"
            desc = route.description or route.summary
            popup_html = (
                f"<b>{name}</b><br>"
                f"Time: {route.duration_formatted}<br>"
                f"Distance: {route.distance_formatted}<br>"
                f"<i>{desc}</i>"
            )

            folium.PolyLine(
                points,
                color=color,
                weight=5,
                opacity=0.7,
                tooltip=f"{name} ({route.duration_formatted})",
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(m)

        # Add Layer Control
        folium.LayerControl().add_to(m)
        
        # Fit bounds
        all_points = [p for r in routes for p in [(c.latitude, c.longitude) for c in r.geometry]]
        if all_points:
            m.fit_bounds(all_points)

        # Save map
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output_file))
        
        logger.info(f"Map saved to {output_file.absolute()}")
        return str(output_file.absolute())
