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
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Pathypotomus Routes</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
<link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.css" />
<style>
  html, body { height: 100%; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif; color: #0f172a; background: #ffffff; }
  header { padding: 12px 16px; border-bottom: 1px solid #e5e7eb; display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
  h1 { font-size: 20px; margin: 0; }
  .sub { color: #475569; font-size: 14px; }
  #map { width: 100%; height: calc(100% - 57px); position: relative; }
  .leaflet-routing-container { 
    background-color: white; 
    padding: 10px; 
    border-radius: 4px; 
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  }
  .legend { position: absolute; top: 12px; right: 12px; background: rgba(255,255,255,0.9); border: 1px solid #e5e7eb; border-radius: 6px; padding: 8px 10px; font-size: 13px; line-height: 1.4; box-shadow: 0 1px 2px rgba(0,0,0,0.08); z-index: 1000; }
  .legend h3 { margin: 0 0 6px 0; font-size: 13px; font-weight: 600; color: #0f172a; }
  .legend .item { display: flex; align-items: center; gap: 8px; margin: 4px 0; }
  .legend .swatch { width: 14px; height: 4px; border-radius: 2px; }
  .swatch.primary { background: #1e90ff; }
  .swatch.alt1 { background: #ff4d4f; }
  .swatch.alt2 { background: #2ecc71; }
</style>
</head>
<body>
  <header>
    <h1>Pathypotomus Routes</h1>
    <span class="sub">Last updated: UPDATED_TIMESTAMP</span>
  </header>
  <div id="map"></div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  <script src="https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.js"></script>
  <script src="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js"></script>
  <script>
    // Helper to parse coordinates from string "lat,lng"
    function parseCoord(str) {
        if (!str) return null;
        const parts = str.split(',').map(Number);
        if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) {
            return L.latLng(parts[0], parts[1]);
        }
        return null;
    }

    const params = new URLSearchParams(window.location.search);
    const pStart = parseCoord(params.get('start'));
    const pEnd = parseCoord(params.get('end'));

    // Defaults
    const defaultStart = [38.7893, -77.1872]; // Springfield, VA
    const defaultEnd = [38.9907, -77.0261];   // Silver Spring, MD
    
    const start = pStart || defaultStart;
    const end = pEnd || defaultEnd;

    const map = L.map('map', {
      zoomControl: true,
      dragging: true,
      scrollWheelZoom: true,
      doubleClickZoom: true,
      boxZoom: true,
      keyboard: true,
      tap: true,
      touchZoom: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Draw primary route and alternatives using OSRM via Leaflet Routing Machine
    const routing = L.Routing.control({
      waypoints: [
        L.latLng(start[0] || start.lat, start[1] || start.lng),
        L.latLng(end[0] || end.lat, end[1] || end.lng)
      ],
      router: L.Routing.osrmv1({
        serviceUrl: 'https://router.project-osrm.org/route/v1'
      }),
      geocoder: L.Control.Geocoder.nominatim(),
      showAlternatives: true,
      reverseWaypoints: true,
      lineOptions: {
        styles: [{ color: '#1e90ff', weight: 6, opacity: 0.9 }]
      },
      altLineOptions: {
        styles: [
          { color: '#ff4d4f', weight: 5, opacity: 0.85 },
          { color: '#2ecc71', weight: 5, opacity: 0.85 }
        ]
      },
      routeWhileDragging: true,
      formatter: new L.Routing.Formatter({ units: 'imperial' })
    }).addTo(map);

    // Update URL when waypoints change
    routing.on('waypointschanged', function(e) {
       const waypoints = e.waypoints;
       if (waypoints.length >= 2) {
           const s = waypoints[0].latLng;
           const d = waypoints[waypoints.length - 1].latLng;
           
           if (s && d) {
               const url = new URL(window.location);
               url.searchParams.set('start', `${s.lat.toFixed(6)},${s.lng.toFixed(6)}`);
               url.searchParams.set('end', `${d.lat.toFixed(6)},${d.lng.toFixed(6)}`);
               window.history.replaceState({}, '', url);
           }
       }
    });

    // Add a simple legend overlay
    const legend = L.control({ position: 'topright' });
    legend.onAdd = function () {
      const div = L.DomUtil.create('div', 'legend');
      div.innerHTML = `
        <h3>Routes</h3>
        <div class="item"><span class="swatch primary"></span>Primary</div>
        <div class="item"><span class="swatch alt1"></span>Alternative 1</div>
        <div class="item"><span class="swatch alt2"></span>Alternative 2</div>
      `;
      return div;
    };
    legend.addTo(map);
  </script>
</body>
</html>
"""

    html = html.replace("UPDATED_TIMESTAMP", updated)

    output_path = output_dir / "index.html"
    output_path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
