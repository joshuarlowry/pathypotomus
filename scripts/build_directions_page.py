from pathlib import Path
from datetime import datetime, timezone


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    output_dir = repo_root / "site"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Ensure GitHub Pages does not run Jekyll
    (output_dir / ".nojekyll").write_text("", encoding="utf-8")

    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")

    html = """<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\" />
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
<title>Directions: Springfield, VA → Silver Spring, MD</title>
<link rel=\"stylesheet\" href=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.css\" integrity=\"sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=\" crossorigin=\"\"/>
<link rel=\"stylesheet\" href=\"https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.css\" />
<style>
  html, body { height: 100%; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif; color: #0f172a; background: #ffffff; }
  header { padding: 12px 16px; border-bottom: 1px solid #e5e7eb; display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
  h1 { font-size: 20px; margin: 0; }
  .sub { color: #475569; font-size: 14px; }
  #map { width: 100%; height: calc(100% - 57px); }
  .leaflet-routing-container { font-size: 14px; }
</style>
</head>
<body>
  <header>
    <h1>Directions: Springfield, VA → Silver Spring, MD</h1>
    <span class=\"sub\">Last updated: UPDATED_TIMESTAMP</span>
  </header>
  <div id=\"map\"></div>

  <script src=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.js\" integrity=\"sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=\" crossorigin=\"\"></script>
  <script src=\"https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.js\"></script>
  <script>
    const start = [38.7893, -77.1872]; // Springfield, VA
    const end = [38.9907, -77.0261];   // Silver Spring, MD

    const map = L.map('map');
    const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const bounds = L.latLngBounds([start, end]).pad(0.2);
    map.fitBounds(bounds);

    L.marker(start).addTo(map).bindPopup('Start: Springfield, VA');
    L.marker(end).addTo(map).bindPopup('End: Silver Spring, MD');

    L.Routing.control({
      waypoints: [
        L.latLng(start[0], start[1]),
        L.latLng(end[0], end[1])
      ],
      router: L.Routing.osrmv1({
        serviceUrl: 'https://router.project-osrm.org/route/v1'
      }),
      showAlternatives: false,
      lineOptions: {
        styles: [{color: '#1e90ff', weight: 6, opacity: 0.8}]
      },
      altLineOptions: {
        styles: [{color: '#87cefa', weight: 4, opacity: 0.7}]
      },
      routeWhileDragging: false,
      addWaypoints: false,
      draggableWaypoints: false,
      fitSelectedRoutes: true,
      show: true,
      formatter: new L.Routing.Formatter({ units: 'imperial' })
    }).addTo(map);
  </script>
</body>
</html>
"""

    html = html.replace("UPDATED_TIMESTAMP", updated)

    output_path = output_dir / "index.html"
    output_path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()