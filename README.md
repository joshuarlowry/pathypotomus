# Pathypotomus - LLM-Powered Route Planner

A self-hosted route planning tool that generates multiple route options with AI-powered descriptions for daily commuters and developers.

## 🎯 Overview

Pathypotomus solves the gap between raw routing data and user-friendly guidance by providing:
- **Multiple route alternatives** between fixed origin/destination points
- **AI-generated route names & descriptions** that capture each route's character
- **Static map visualization** with color-coded route options
- **Embeddable HTML output** for integration into other applications

Perfect for commuters who want meaningful route context beyond just "X minutes via Highway 1" and developers building transportation apps who need an easy-to-integrate routing solution.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/pathypotomus.git
cd pathypotomus

# Set up environment
cp .env.example .env
# Edit .env with your origin/destination addresses

# Run with Docker
docker-compose up

# Or run locally
pip install -r requirements.txt
python src/main.py
```

## 📋 Features (MVP v1)

- ✅ **OSRM-Powered Routing**: OSRM client implemented and tested (unit). Integration with live OSRM pending geocoding step
- ✅ **AI Route Descriptions**: LLM-generated names and descriptions for each route
- ✅ **Static Map Output**: Visual route comparison with color-coded paths
- ✅ **Self-Hosted**: Complete solution runs on your infrastructure
- ✅ **Embeddable**: HTML output ready for integration

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Config        │    │   Routing    │    │   LLM Service   │
│ (Origin/Dest)   │───▶│   Engine     │───▶│  (Descriptions) │
│                 │    │   (OSRM)     │    │                 │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                      │
                                                      ▼
                                            ┌─────────────────┐
                                            │  HTML Generator │
                                            │  (Static Map)   │
                                            └─────────────────┘
```

## 📚 Documentation

- [**MVP Development Checklist**](docs/mvp-checklist.md) - Phased development plan
- [**Technical Architecture**](docs/architecture.md) - System design and components
- [**API Specifications**](docs/api-specs.md) - Data models and interfaces
- [**Deployment Guide**](docs/deployment.md) - Self-hosting setup instructions
- [**Development Guidelines**](docs/development.md) - Code standards and contribution workflow

## 🎯 Target Users

**Everyday Commuter**: Tech-savvy commuters seeking multiple route options with meaningful context for their daily travels.

**App Developer**: Developers building transportation apps who need a self-hosted routing solution with rich descriptions.

## 🛣️ Roadmap

**v1 (MVP)**: Fixed origin/destination, static HTML output, basic AI descriptions
**v2**: Interactive UI, multiple transportation modes, user preferences
**v3**: Real-time data, multi-user support, hosted service option

## 🤝 Contributing

See [Development Guidelines](docs/development.md) for setup instructions and contribution workflow.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
