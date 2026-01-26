from pathlib import Path
from datetime import datetime, timezone

def get_base_html(title, content, updated_time, active_page, extra_scripts=""):
    nav_links = {
        "home": "index.html",
        "map": "map.html",
        "about": "about.html"
    }
    
    nav_items = []
    for key, link in nav_links.items():
        active_class = 'active' if key == active_page else ''
        nav_items.append(f'<a href="{link}" class="{active_class}">{key.capitalize()}</a>')
    
    nav_html = "\n".join(nav_items)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title} | Pathypotomus</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
<link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.css" />
<style>
  html, body {{ height: 100%; margin: 0; padding: 0; display: flex; flex-direction: column; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif; color: #0f172a; background: #ffffff; }}
  
  /* Header */
  header {{ padding: 12px 20px; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between; background: #fff; box-shadow: 0 1px 2px rgba(0,0,0,0.05); z-index: 1000; }}
  .brand {{ font-weight: 700; font-size: 18px; display: flex; align-items: center; gap: 20px; }}
  .brand a {{ text-decoration: none; color: inherit; }}
  .nav {{ display: flex; gap: 20px; }}
  .nav a {{ text-decoration: none; color: #64748b; font-size: 14px; font-weight: 500; transition: color 0.2s; }}
  .nav a:hover {{ color: #0f172a; }}
  .nav a.active {{ color: #0f172a; font-weight: 600; }}
  .meta {{ color: #94a3b8; font-size: 12px; }}

  /* Main */
  main {{ flex: 1; position: relative; overflow-y: auto; }}
  
  /* Map Specific */
  #map {{ width: 100%; height: 100%; }}
  
  /* Content Pages */
  .container {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
  h1 {{ font-size: 32px; margin-bottom: 16px; letter-spacing: -0.5px; }}
  p {{ line-height: 1.6; color: #334155; margin-bottom: 24px; }}
  .btn {{ display: inline-block; background: #2563eb; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 500; transition: background 0.2s; }}
  .btn:hover {{ background: #1d4ed8; }}

  /* Leaflet Overrides */
  .leaflet-routing-container {{ 
    background-color: white; 
    padding: 10px; 
    border-radius: 8px; 
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
    border: none;
    max-height: 80vh;
    overflow-y: auto;
  }}
  .legend {{ position: absolute; top: 12px; right: 12px; background: rgba(255,255,255,0.95); border-radius: 6px; padding: 12px; font-size: 13px; line-height: 1.4; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); z-index: 1000; backdrop-filter: blur(4px); }}
  .legend h3 {{ margin: 0 0 8px 0; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; }}
  .legend .item {{ display: flex; align-items: center; gap: 8px; margin: 4px 0; }}
  .legend .swatch {{ width: 16px; height: 4px; border-radius: 2px; }}
  .swatch.primary {{ background: #1e90ff; }}
  .swatch.alt1 {{ background: #ff4d4f; }}
  .swatch.alt2 {{ background: #2ecc71; }}
</style>
</head>
<body>
  <header>
    <div class="brand">
        <a href="index.html">Pathypotomus</a>
        <nav class="nav">
            {nav_html}
        </nav>
    </div>
    <span class="meta">Last build: {updated_time}</span>
  </header>
  <main>
    {content}
  </main>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  <script src="https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.js"></script>
  <script src="https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js"></script>
  {extra_scripts}
</body>
</html>
"""

def main():
    repo_root = Path(__file__).resolve().parents[1]
    output_dir = repo_root / "site"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    (output_dir / ".nojekyll").write_text("", encoding="utf-8")
    
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    # 1. Generate Index Page
    index_content = """
    <div class="container">
        <h1>Welcome to Pathypotomus Routes</h1>
        <p>Explore optimal routes with our intelligent routing engine. Visualize paths, compare alternatives, and get detailed directions.</p>
        <a href="map.html" class="btn">Launch Map Planner &rarr;</a>
        
        <div style="margin-top: 40px; padding: 24px; background: #f1f5f9; border-radius: 8px;">
            <h3 style="margin-top: 0;">How it works</h3>
            <p style="margin-bottom: 0;">Pathypotomus uses OSRM for routing and Nominatim for geocoding to help you find the best way from A to B.</p>
        </div>
    </div>
    """
    (output_dir / "index.html").write_text(
        get_base_html("Home", index_content, updated, "home"), 
        encoding="utf-8"
    )

    # 2. Generate Map Page (Existing Logic)
    map_content = '<div id="map"></div>'
    map_script = """
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
    """
    (output_dir / "map.html").write_text(
        get_base_html("Route Planner", map_content, updated, "map", map_script), 
        encoding="utf-8"
    )

    # 3. Generate About Page
    about_content = """
    <div class="container">
        <h1>About Pathypotomus</h1>
        <p>Pathypotomus is an experimental route planning tool designed to explore the intersection of classical routing algorithms (OSRM) and modern AI capabilities.</p>
        <p>Our goal is to provide not just directions, but context-aware routing suggestions.</p>
        <p>Built with Python, Leaflet, and GitHub Actions.</p>
    </div>
    """
    (output_dir / "about.html").write_text(
        get_base_html("About", about_content, updated, "about"), 
        encoding="utf-8"
    )
    
    print(f"Site generated in {output_dir}")

if __name__ == "__main__":
    main()
