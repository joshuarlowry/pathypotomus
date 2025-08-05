# Deployment Guide

Complete setup and deployment instructions for self-hosting the LLM-Powered Route Planner.

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

The fastest way to get up and running with all services:

```bash
# Clone the repository
git clone https://github.com/your-org/pathypotomus.git
cd pathypotomus

# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # Set your origin/destination addresses and API keys

# Start all services
docker-compose up -d

# Generate routes
docker-compose exec pathypotomus python -m pathypotomus.main

# View output
open output/routes.html
```

### Option 2: Local Development Setup

For development or custom installations:

```bash
# Clone and setup
git clone https://github.com/your-org/pathypotomus.git
cd pathypotomus

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the application
python -m pathypotomus.main
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with your configuration:

```bash
# Required Settings
ORIGIN_ADDR="123 Main Street, Springfield, IL, USA"
DEST_ADDR="456 Oak Avenue, Shelbyville, IL, USA"

# Optional - OSRM Service
OSRM_URL="https://router.project-osrm.org"  # Public demo server
# OSRM_URL="http://localhost:5000"  # Local OSRM instance

# Optional - LLM Service
LLM_API_KEY="your-openai-api-key-here"
LLM_MODEL="gpt-3.5-turbo"  # or "gpt-4" for better quality

# Optional - Output Settings
OUTPUT_PATH="./output/routes.html"
MAX_ROUTES=3

# Optional - Advanced Settings
GEOCODING_PROVIDER="nominatim"
MAP_ZOOM=12
ROUTE_COLORS="#e74c3c,#3498db,#2ecc71"
```

### Configuration Options Explained

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ORIGIN_ADDR` | ✅ | - | Starting address for routes |
| `DEST_ADDR` | ✅ | - | Destination address for routes |
| `OSRM_URL` | ❌ | Public demo | OSRM routing service URL |
| `LLM_API_KEY` | ❌ | - | OpenAI API key for descriptions |
| `LLM_MODEL` | ❌ | gpt-3.5-turbo | LLM model to use |
| `OUTPUT_PATH` | ❌ | routes.html | Output file path |
| `MAX_ROUTES` | ❌ | 3 | Maximum routes to generate |
| `GEOCODING_PROVIDER` | ❌ | nominatim | Geocoding service |
| `MAP_ZOOM` | ❌ | 12 | Default map zoom level |
| `ROUTE_COLORS` | ❌ | Red,Blue,Green | Route colors (hex codes) |

## 🐳 Docker Deployment

### Full Stack with Docker Compose

The `docker-compose.yml` includes all necessary services:

```yaml
version: '3.8'

services:
  # OSRM routing engine with local data
  osrm:
    image: osrm/osrm-backend:latest
    volumes:
      - ./data:/data
    ports:
      - "5000:5000"
    command: osrm-routed --algorithm mld /data/map.osrm
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Main application
  pathypotomus:
    build: .
    depends_on:
      osrm:
        condition: service_healthy
    environment:
      - OSRM_URL=http://osrm:5000
      - ORIGIN_ADDR=${ORIGIN_ADDR}
      - DEST_ADDR=${DEST_ADDR}
      - LLM_API_KEY=${LLM_API_KEY}
      - LLM_MODEL=${LLM_MODEL:-gpt-3.5-turbo}
    volumes:
      - ./output:/app/output
      - ./config:/app/config
    restart: unless-stopped

  # Optional: Nginx for serving static files
  nginx:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./output:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - pathypotomus
```

### Docker Commands

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f pathypotomus

# Generate new routes
docker-compose exec pathypotomus python -m pathypotomus.main

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose build pathypotomus
docker-compose up -d pathypotomus
```

## 🗺️ OSRM Setup

### Option 1: Use Public OSRM Demo

Easiest setup for testing:

```bash
# Set in .env file
OSRM_URL="https://router.project-osrm.org"
```

**Limitations:**
- Rate limited (not suitable for production)
- No guarantee of availability
- Limited to basic routing profiles

### Option 2: Self-Hosted OSRM

For production use, run your own OSRM instance:

#### Step 1: Download Map Data

```bash
# Create data directory
mkdir -p data

# Download OSM data for your region
# Example: Illinois, USA
wget http://download.geofabrik.de/north-america/us/illinois-latest.osm.pbf -O data/map.osm.pbf
```

#### Step 2: Prepare OSRM Data

```bash
# Extract, partition, and customize
docker run -t -v "${PWD}/data:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/map.osm.pbf
docker run -t -v "${PWD}/data:/data" osrm/osrm-backend osrm-partition /data/map.osrm
docker run -t -v "${PWD}/data:/data" osrm/osrm-backend osrm-customize /data/map.osrm
```

#### Step 3: Run OSRM Server

```bash
# Start OSRM server
docker run -t -i -p 5000:5000 -v "${PWD}/data:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/map.osrm

# Test the server
curl "http://localhost:5000/route/v1/driving/-87.6298,41.8781;-87.6344,41.8708?overview=false"
```

#### Step 4: Update Configuration

```bash
# Set in .env file
OSRM_URL="http://localhost:5000"
```

### OSRM Performance Tuning

For better performance with large datasets:

```bash
# Increase memory allocation
docker run -t -i -p 5000:5000 -v "${PWD}/data:/data" \
  --memory=4g \
  osrm/osrm-backend osrm-routed --algorithm mld /data/map.osrm --max-matching-size 10000
```

## 🤖 LLM Service Setup

### OpenAI API Setup

1. **Get API Key:**
   - Visit [OpenAI API](https://platform.openai.com/api-keys)
   - Create new API key
   - Copy key to `.env` file

2. **Choose Model:**
   ```bash
   # Faster, cheaper
   LLM_MODEL="gpt-3.5-turbo"
   
   # Better quality, more expensive
   LLM_MODEL="gpt-4"
   
   # Latest models
   LLM_MODEL="gpt-4-turbo-preview"
   ```

3. **Monitor Usage:**
   - Check usage at [OpenAI Usage Dashboard](https://platform.openai.com/usage)
   - Set billing limits to avoid unexpected charges

### Alternative LLM Providers

#### Anthropic Claude (Future Support)

```bash
# When supported
LLM_PROVIDER="anthropic"
LLM_API_KEY="your-anthropic-key"
LLM_MODEL="claude-3-sonnet"
```

#### Local LLM with Ollama (Future Support)

```bash
# Run local LLM
docker run -d -p 11434:11434 ollama/ollama
docker exec -it ollama ollama pull llama2

# Configure
LLM_PROVIDER="ollama"
LLM_URL="http://localhost:11434"
LLM_MODEL="llama2"
```

## 🌐 Production Deployment

### Server Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB (8GB recommended with local OSRM)
- Storage: 10GB (more for larger OSM datasets)
- Network: Stable internet for LLM API calls

**Recommended for Production:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: SSD with 50GB+ (for full regional OSM data)
- Network: High bandwidth for map data processing

### Production Docker Compose

```yaml
version: '3.8'

services:
  osrm:
    image: osrm/osrm-backend:latest
    volumes:
      - osrm_data:/data
    ports:
      - "127.0.0.1:5000:5000"  # Bind to localhost only
    command: osrm-routed --algorithm mld /data/map.osrm
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  pathypotomus:
    build: .
    depends_on:
      osrm:
        condition: service_healthy
    environment:
      - OSRM_URL=http://osrm:5000
      - ORIGIN_ADDR=${ORIGIN_ADDR}
      - DEST_ADDR=${DEST_ADDR}
      - LLM_API_KEY=${LLM_API_KEY}
      - LLM_MODEL=${LLM_MODEL}
      - OUTPUT_PATH=/app/output/routes.html
    volumes:
      - route_output:/app/output
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - route_output:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - pathypotomus
    restart: unless-stopped

volumes:
  osrm_data:
  route_output:
```

### SSL/HTTPS Setup

1. **Generate SSL Certificate:**
   ```bash
   # Using Let's Encrypt
   certbot certonly --standalone -d your-domain.com
   
   # Copy certificates
   mkdir ssl
   cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/
   cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/
   ```

2. **Nginx SSL Configuration:**
   ```nginx
   server {
       listen 443 ssl http2;
       server_name your-domain.com;
       
       ssl_certificate /etc/nginx/ssl/fullchain.pem;
       ssl_certificate_key /etc/nginx/ssl/privkey.pem;
       
       location / {
           root /usr/share/nginx/html;
           index routes.html;
       }
   }
   
   server {
       listen 80;
       server_name your-domain.com;
       return 301 https://$server_name$request_uri;
   }
   ```

### Automated Route Generation

Set up cron job for regular route updates:

```bash
# Edit crontab
crontab -e

# Add job to regenerate routes daily at 6 AM
0 6 * * * cd /path/to/pathypotomus && docker-compose exec -T pathypotomus python -m pathypotomus.main
```

### Monitoring and Logging

1. **Application Logs:**
   ```bash
   # View application logs
   docker-compose logs -f pathypotomus
   
   # Export logs to file
   docker-compose logs pathypotomus > pathypotomus.log
   ```

2. **Health Checks:**
   ```bash
   # Check OSRM health
   curl http://localhost:5000/health
   
   # Check if routes file exists and is recent
   ls -la output/routes.html
   ```

3. **Resource Monitoring:**
   ```bash
   # Monitor container resources
   docker stats
   
   # Check disk usage
   du -sh data/  # OSRM data size
   ```

## 🔧 Troubleshooting

### Common Issues

#### 1. Geocoding Failures

**Error:** `GeocodingError: Address not found`

**Solutions:**
- Check address format (include city, state, country)
- Try coordinates instead: `ORIGIN_ADDR="41.8781,-87.6298"`
- Use more specific addresses

#### 2. OSRM Connection Issues

**Error:** `RoutingError: OSRM request failed: HTTP 500`

**Solutions:**
```bash
# Check OSRM service status
docker-compose logs osrm

# Restart OSRM service
docker-compose restart osrm

# Verify OSRM data integrity
docker-compose exec osrm ls -la /data/
```

#### 3. LLM API Failures

**Error:** `LLMError: LLM API call failed`

**Solutions:**
- Check API key validity
- Verify billing status on OpenAI dashboard
- Check rate limits
- Use fallback descriptions (set `LLM_API_KEY=""`)

#### 4. Memory Issues

**Error:** `Container killed (OOMKilled)`

**Solutions:**
```bash
# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G  # Increase from 4G

# Check available memory
free -h

# Reduce OSRM data size (use smaller region)
```

#### 5. Permission Issues

**Error:** `Permission denied: output/routes.html`

**Solutions:**
```bash
# Fix output directory permissions
sudo chown -R $USER:$USER output/
chmod 755 output/

# Or run with proper user in Docker
docker-compose exec --user $(id -u):$(id -g) pathypotomus python -m pathypotomus.main
```

### Performance Optimization

1. **OSRM Optimization:**
   ```bash
   # Use MLD algorithm for faster routing
   osrm-routed --algorithm mld /data/map.osrm
   
   # Increase shared memory
   --max-matching-size 10000
   ```

2. **Application Optimization:**
   ```python
   # Enable parallel LLM processing
   MAX_CONCURRENT_LLM_CALLS=3
   
   # Cache geocoding results
   ENABLE_GEOCODING_CACHE=true
   ```

3. **System Optimization:**
   ```bash
   # Use SSD for OSRM data
   # Increase system memory
   # Use faster internet connection for LLM APIs
   ```

### Backup and Recovery

1. **Backup Configuration:**
   ```bash
   # Backup configuration and data
   tar -czf pathypotomus-backup.tar.gz .env docker-compose.yml data/ output/
   ```

2. **Restore from Backup:**
   ```bash
   # Extract backup
   tar -xzf pathypotomus-backup.tar.gz
   
   # Restore services
   docker-compose up -d
   ```

## 📊 Monitoring and Maintenance

### Health Monitoring

Create a monitoring script:

```bash
#!/bin/bash
# health-check.sh

# Check OSRM service
if ! curl -s http://localhost:5000/health > /dev/null; then
    echo "OSRM service is down"
    docker-compose restart osrm
fi

# Check if routes file is recent (less than 24 hours old)
if test $(find output/routes.html -mtime +1); then
    echo "Routes file is outdated, regenerating..."
    docker-compose exec -T pathypotomus python -m pathypotomus.main
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Disk usage is high: ${DISK_USAGE}%"
fi
```

### Regular Maintenance

1. **Update Dependencies:**
   ```bash
   # Update Docker images
   docker-compose pull
   docker-compose up -d
   
   # Update Python packages
   pip install -r requirements.txt --upgrade
   ```

2. **Clean Up:**
   ```bash
   # Remove old Docker images
   docker image prune -a
   
   # Clean up logs
   docker-compose logs --since 7d > recent.log
   ```

3. **Data Updates:**
   ```bash
   # Update OSM data monthly
   wget http://download.geofabrik.de/north-america/us/illinois-latest.osm.pbf -O data/map.osm.pbf
   
   # Rebuild OSRM data
   docker-compose down osrm
   # Re-run OSRM data preparation steps
   docker-compose up -d osrm
   ```

This comprehensive deployment guide covers everything needed to successfully self-host the LLM-Powered Route Planner in various environments.