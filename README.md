# Geopolitical Conflict Analyzer

An automated pipeline for extracting, analyzing, and visualizing geopolitical events from social media sources using Large Language Models and interactive 3D visualization.

## Overview

This system ingests posts from Telegram channels, processes them through an LLM-based extraction pipeline to identify actor-target relationships, grounds entities to sovereign states, and visualizes the resulting conflict network on an interactive 3D globe.

## Architecture

### Backend (Python/FastAPI)
- **Data Ingestion**: Telethon-based Telegram API client for event collection
- **LLM Processing**: Ollama integration for actor-target extraction and state grounding
- **Storage**: PostgreSQL database with job management and processing status tracking
- **API**: RESTful endpoints for data access, processing control, and visualization

### Frontend (React/Vite)
- **Visualization**: Deck.gl-powered 3D globe with interactive arc layer
- **Filtering**: Time-range and event-type selection
- **Admin Panel**: Processing job control and status monitoring

## Features

- Automated event ingestion from configured Telegram channels
- Sentence-level actor-target-event extraction using local LLM
- Entity grounding to ISO3 country codes with coordinate mapping
- Time-filtered relationship aggregation
- Real-time 3D visualization of geopolitical interactions
- Background job processing with status tracking

## Installation

### Prerequisites
- Python 3.14+
- Node.js 18+
- PostgreSQL 14+
- Ollama with mistral:instruct model

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your database credentials and API keys

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend/geop-globe

# Install dependencies
npm install

# Start development server
npm run dev
```

## Data Model

### Event Ontology

| Event Type | Description |
|------------|-------------|
| ATTACK | Kinetic or physical attacks, strikes, targeting |
| THREAT | Explicit threats or warnings of action |
| COERCIVE_ACTION | Sanctions, tariffs, arms sales, funding cuts |
| DIPLOMATIC_ACTION | Agreements, MOUs, formal diplomatic acts |
| PROTEST | Organized public protests or unrest |
| CYBER_OPERATION | Cyber attacks or cyber coercion |
| TERRORISM | Terrorist attacks or operations |

### Entity Types

| Type | Description | Examples |
|------|-------------|----------|
| STATE | Sovereign states | USA, Russia, Ukraine |
| STATE_EXECUTIVE | Government/leadership | Trump administration, Kremlin |
| INT_ORG | International organizations | UN, EU, NATO |
| NON_STATE_ACTOR | Armed groups, militias | Hamas, ISIS |
| ORG | Companies, institutions | Gazprom, Lockheed Martin |
| LOCATION | Cities, regions | Gaza, Donetsk |

## API Endpoints

### Data Ingestion
- `POST /api/reboot-full` - Full historical data refresh
- `POST /api/refresh-incremental` - Incremental update
- `POST /api/fetch-period` - Custom date range ingestion

### LLM Processing
- `POST /api/process` - Start LLM extraction/grounding job
  - Query params: `mode` (all, last_n, missing_extraction, missing_states), `limit`
- `GET /api/jobs/{job_name}` - Check job status
- `POST /api/jobs/{job_name}/reset` - Reset stuck job

### Visualization
- `GET /api/relations` - Get actor-target relations
  - Query params: `from` (date), `to` (date)

## Processing Pipeline

1. **Initialization**: New events are split into sentences and inserted into `actortargetevents` table
2. **Extraction**: LLM extracts actor, target, and event type from each sentence
3. **Grounding**: LLM maps actor/target to sovereign states and retrieves ISO3 codes
4. **Aggregation**: Relations are grouped by actor-state, target-state, and event type
5. **Visualization**: Frontend fetches aggregated relations and renders arcs on globe

## Database Schema

### Tables
- `events`: Raw ingested posts with metadata
- `actortargetevents`: Sentence-level extractions with actor/target/event/state data
- `states`: Country reference data with ISO3 codes and coordinates
- `jobs`: Processing job status tracking

## Configuration

### Backend
```
DATABASE_URL=postgresql://user:pass@localhost/dbname
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
OLLAMA_BASE_URL=http://localhost:11434
```

### Frontend
```javascript
const API_BASE = "http://127.0.0.1:8000/api";
```

## Development

### Running Tests
```bash
cd backend
pytest
```

### Code Quality
```bash
# Backend
flake8 .
black .

# Frontend
npm run lint
```

## Legal and Ethical Notice

- Source content originates from publicly accessible Telegram channels
- No private, restricted, or paywalled content is included
- Data is processed for research and analytical purposes only
- Users are responsible for compliance with applicable data protection regulations

## License

This project is provided for research and educational purposes.

## Contributing

Contributions are welcome. Please open an issue or submit a pull request for any improvements or bug fixes.
