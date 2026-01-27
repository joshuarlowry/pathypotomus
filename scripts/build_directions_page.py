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
  .btn {{ display: inline-block; background: #2563eb; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 500; transition: background 0.2s; cursor: pointer; border: none; font-size: 14px; }}
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
  
  /* Hide detailed instructions on map view */
  .leaflet-routing-container table {{ display: none; }}
  
  .legend {{ position: absolute; top: 12px; right: 12px; background: rgba(255,255,255,0.95); border-radius: 6px; padding: 12px; font-size: 13px; line-height: 1.4; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); z-index: 1000; backdrop-filter: blur(4px); }}
  .legend h3 {{ margin: 0 0 8px 0; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; }}
  .legend .item {{ display: flex; align-items: center; gap: 8px; margin: 4px 0; }}
  .legend .swatch {{ width: 16px; height: 4px; border-radius: 2px; }}
  .swatch.primary {{ background: #1e90ff; }}
  .swatch.alt1 {{ background: #ff4d4f; }}
  .swatch.alt2 {{ background: #2ecc71; }}

  /* Progressive Disclosure UI */
  .hidden {{ display: none !important; }}
  
  #search-overlay {{
    position: fixed; top: 53px; /* Below header */ left: 0; width: 100%; height: calc(100% - 53px);
    background: #f8fafc; z-index: 2000;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
  }}
  .search-box {{
    background: white; padding: 40px; border-radius: 12px;
    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
    width: 90%; max-width: 400px;
    border: 1px solid #e2e8f0;
  }}
  .search-box h2 {{ margin-top: 0; margin-bottom: 24px; font-size: 24px; text-align: center; }}
  .input-group {{ margin-bottom: 16px; }}
  .input-group label {{ display: block; margin-bottom: 8px; font-weight: 500; font-size: 14px; color: #475569; }}
  .input-group input {{ width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 16px; box-sizing: border-box; }}
  .input-group input:focus {{ outline: none; border-color: #2563eb; ring: 2px solid #2563eb; }}
  
  #view-directions-btn {{
    position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%);
    z-index: 1000;
    padding: 12px 24px; background: #2563eb; color: white;
    border-radius: 30px; font-weight: 600; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    cursor: pointer; border: none; font-size: 16px;
    display: none;
    transition: transform 0.2s;
  }}
  #view-directions-btn:hover {{ transform: translateX(-50%) scale(1.05); background: #1d4ed8; }}
  
  #modal-overlay {{
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.5); z-index: 3000;
    display: none; align-items: center; justify-content: center;
    backdrop-filter: blur(2px);
  }}
  #modal-content {{
    background: white; width: 90%; max-width: 600px; max-height: 80vh;
    border-radius: 12px; overflow: hidden; display: flex; flex-direction: column;
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
  }}
  .modal-header {{ padding: 16px 24px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }}
  .modal-header h3 {{ margin: 0; font-size: 18px; color: #1e293b; }}
  .modal-close {{ background: none; border: none; font-size: 28px; cursor: pointer; color: #64748b; line-height: 1; }}
  .modal-close:hover {{ color: #0f172a; }}
  .modal-body {{ padding: 20px; overflow-y: auto; flex: 1; }}
  
  /* Modal Table Overrides */
  #modal-content table {{ display: table; width: 100%; border-collapse: collapse; }}
  #modal-content tr {{ border-bottom: 1px solid #f1f5f9; }}
  #modal-content td {{ padding: 12px 8px; font-size: 14px; color: #334155; }}
  #modal-content tr:last-child {{ border-bottom: none; }}
  
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

    # 2. Generate Map Page
    map_content = """
    <div id="search-overlay">
        <div class="search-box">
            <h2>Plan Your Route</h2>
            <div class="input-group">
                <label for="start-input">Start Location</label>
                <input type="text" id="start-input" placeholder="e.g. Springfield, VA" onkeypress="handleEnter(event)">
            </div>
            <div class="input-group">
                <label for="end-input">Destination</label>
                <input type="text" id="end-input" placeholder="e.g. Silver Spring, MD" onkeypress="handleEnter(event)">
            </div>
            <button id="search-btn" class="btn" onclick="startSearch()" style="width: 100%;">Get Directions</button>
            <p id="search-error" style="color: #ef4444; margin-top: 12px; font-size: 14px; display: none;"></p>
        </div>
    </div>

    <div id="map"></div>
    
    <button id="view-directions-btn" onclick="openModal()">View Step-by-Step Directions</button>
    
    <div id="modal-overlay" onclick="if(event.target === this) closeModal()">
        <div id="modal-content">
            <div class="modal-header">
                <h3>Detailed Directions</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body" id="modal-body-content">
                <!-- Directions will be populated here -->
                <p style="color: #64748b; text-align: center;">Select a route to view directions.</p>
            </div>
        </div>
    </div>
    """
    
    map_script = """
    <script>
    // --- Configuration & Helpers ---
    function parseCoord(str) {
        if (!str) return null;
        const parts = str.split(',').map(Number);
        if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) {
            return L.latLng(parts[0], parts[1]);
        }
        return null;
    }

    // --- DOM Elements ---
    const searchOverlay = document.getElementById('search-overlay');
    const startInput = document.getElementById('start-input');
    const endInput = document.getElementById('end-input');
    const searchBtn = document.getElementById('search-btn');
    const errorMsg = document.getElementById('search-error');
    const viewBtn = document.getElementById('view-directions-btn');
    const modalOverlay = document.getElementById('modal-overlay');
    const modalBody = document.getElementById('modal-body-content');

    // --- State & Initialization ---
    const params = new URLSearchParams(window.location.search);
    const pStart = parseCoord(params.get('start'));
    const pEnd = parseCoord(params.get('end'));
    const hasValidParams = pStart && pEnd;

    // Initialize Map
    const map = L.map('map', {
      zoomControl: true,
      dragging: true,
      scrollWheelZoom: true,
      doubleClickZoom: true,
      touchZoom: true
    });
    
    // Default view (will be updated if params exist)
    map.setView([38.9072, -77.0369], 10); // DC Area default

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Geocoder instance
    const geocoder = L.Control.Geocoder.nominatim();

    // --- Logic ---
    
    function handleEnter(e) {
        if(e.key === 'Enter') startSearch();
    }

    // Promisified Geocode
    function geocodeQuery(query) {
        return new Promise((resolve, reject) => {
            // Set a timeout to prevent infinite hanging
            const timeoutId = setTimeout(() => {
                reject("Geocoding timed out. Please check your internet connection.");
            }, 10000);

            try {
                geocoder.geocode(query, (results) => {
                    clearTimeout(timeoutId);
                    if (results && results.length > 0) {
                        resolve(results[0]);
                    } else {
                        reject("Could not find location: " + query);
                    }
                });
            } catch (e) {
                clearTimeout(timeoutId);
                reject("Geocoding error: " + e);
            }
        });
    }

    async function startSearch() {
        const sVal = startInput.value.trim();
        const eVal = endInput.value.trim();
        
        if (!sVal || !eVal) {
            errorMsg.textContent = "Please enter both locations.";
            errorMsg.style.display = 'block';
            return;
        }

        errorMsg.style.display = 'none';
        searchBtn.disabled = true;
        searchBtn.textContent = "Searching...";
        
        try {
            const [startRes, endRes] = await Promise.all([
                geocodeQuery(sVal),
                geocodeQuery(eVal)
            ]);
            
            const sLat = startRes.center.lat.toFixed(6);
            const sLng = startRes.center.lng.toFixed(6);
            const eLat = endRes.center.lat.toFixed(6);
            const eLng = endRes.center.lng.toFixed(6);

            // Update URL and Reload/Re-init
            const newUrl = new URL(window.location);
            newUrl.searchParams.set('start', `${sLat},${sLng}`);
            newUrl.searchParams.set('end', `${eLat},${eLng}`);
            window.history.pushState({}, '', newUrl);
            
            // Apply Search
            initRouting(startRes.center, endRes.center);
            searchOverlay.classList.add('hidden');
            
        } catch (err) {
            errorMsg.textContent = "Error: " + err;
            errorMsg.style.display = 'block';
        } finally {
            searchBtn.disabled = false;
            searchBtn.textContent = "Get Directions";
        }
    }

    let routingControl = null;

    function initRouting(sLatLng, eLatLng) {
        if (routingControl) {
            map.removeControl(routingControl);
        }

        routingControl = L.Routing.control({
          waypoints: [sLatLng, eLatLng],
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
        
        // When routes are found, show the details button
        routingControl.on('routesfound', function(e) {
            viewBtn.style.display = 'block';
            // Also populate modal content if it's open? 
            // Better to clone on demand in openModal()
        });

        // Update URL on drag
        routingControl.on('waypointschanged', function(e) {
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
    }

    // Modal Functions
    function openModal() {
        // Find the LRM itinerary container
        // LRM puts active route instructions in a div with class 'leaflet-routing-alt'
        // But there might be multiple (hidden). We want the visible one from the sidebar? 
        // Or actually, we hid them all with CSS.
        // We need to find the one corresponding to the selected route. 
        
        // Actually LRM puts them in the DOM. The one that corresponds to the selected route is usually not hidden by LRM itself, but we hid it with our custom CSS.
        // We can just grab all 'leaflet-routing-alt' divs and clone them? 
        // Or better: LRM adds a class 'leaflet-routing-alt-minimized' or similar? 
        // Let's just clone the entire '.leaflet-routing-container' content but strip the inputs?
        
        // The container has header (inputs) and then alternatives.
        // Let's look for '.leaflet-routing-alt' elements.
        
        const container = document.querySelector('.leaflet-routing-container');
        if (!container) return;
        
        const alts = container.querySelectorAll('.leaflet-routing-alt');
        modalBody.innerHTML = ''; // clear
        
        if (alts.length === 0) {
            modalBody.innerHTML = '<p>No directions available yet.</p>';
            return;
        }

        // Clone all alternatives (LRM handles showing/hiding them based on selection usually, but we might have interfered with CSS)
        // If we only hid table, the header summary is visible in sidebar.
        // In modal we want everything.
        
        alts.forEach(alt => {
             // We only want to show the one that is currently "active" in LRM logic.
             // LRM toggles 'display' style on them.
             // Since we overrode display:none for table, we need to respect the parent div's display state if LRM sets it.
             // LRM sets style="display: block/none" on the .leaflet-routing-alt div.
             
             // Check if it's not hidden by inline style
             if (alt.style.display !== 'none') {
                 const clone = alt.cloneNode(true);
                 modalBody.appendChild(clone);
             }
        });
        
        // Fallback if none found (e.g. first load) - just take the first one
        if (modalBody.children.length === 0 && alts.length > 0) {
            const clone = alts[0].cloneNode(true);
            modalBody.appendChild(clone);
        }
        
        modalOverlay.style.display = 'flex';
    }

    function closeModal() {
        modalOverlay.style.display = 'none';
    }

    // --- Bootstrap ---
    if (hasValidParams) {
        searchOverlay.classList.add('hidden');
        initRouting(pStart, pEnd);
    } else {
        // Show search overlay (default)
        // If start/end not provided, maybe set inputs to defaults?
        // User asked for "start and end search first". 
        // Let's pre-fill with defaults for demo purposes but let user search.
        // startInput.value = "Springfield, VA";
        // endInput.value = "Silver Spring, MD";
    }
    
    // Add Legend (same as before)
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
