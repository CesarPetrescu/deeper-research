# deeper-research

This repository contains a research assistant built around the `deep_crawler` package, featuring both a CLI and web interface. The system uses a unified configuration approach with a single `config.toml` file.

## Features

- **Unified Configuration**: Single `config.toml` file for all components
- **Web Interface**: React-based UI with live research streaming
- **Persistent Storage**: SQLite database stores all research reports
- **Multiple Export Formats**: Download reports as Markdown, PDF, or DOCX
- **Research History**: View and download previous research results
- **Real-time Updates**: Stream research progress in the browser
- **API Server**: Flask-based backend with RESTful endpoints

## Quick Start

1. **Install Dependencies**:
   ```bash
   # Python dependencies
   pip install -r requirements.txt
   
   # UI dependencies  
   cd ui && npm install && npm run build && cd ..
   ```

2. **Configure**: Edit `config.toml` (see [Configuration Guide](CONFIGURATION.md))

3. **Start Services**:
   ```bash
   ./start_services.sh
   ```

4. **Access**: Open http://localhost:3000 in your browser

## Configuration

The system uses a unified configuration in `config.toml`. See [CONFIGURATION.md](CONFIGURATION.md) for details.

Key settings:
- `[server]` - API and UI server ports and hosts
- `[api]` - LLM and embedding model configuration  
- `[search]` - Search engine settings
- `[firecrawl]` - Web crawling configuration

## Project Structure

```
├── config.toml                    # Unified configuration
├── start_services.sh              # Start all services
├── show_config.sh                 # View current configuration  
├── CONFIGURATION.md               # Configuration guide
├── deep_crawler/                  # Core research engine
│   ├── cli.py                     # Command-line interface
│   ├── api_server.py              # Flask API server
│   ├── crawler/                   # Web crawling
│   ├── indexing/                  # Vector storage & embeddings
│   └── llm/                       # Language model integration
└── ui/                            # Web interface
    ├── config.json                # Auto-generated UI config
    ├── server.js                  # Express proxy server
    ├── public/app.jsx              # React frontend
    └── dist/                      # Built frontend assets
```

## API Endpoints

- `GET /api/research?q=<question>` - Stream research results (SSE)
- `GET /api/reports` - List previous research reports
- `GET /api/reports/<id>` - Get specific research report
- `GET /api/download/<id>/<format>` - Download report (markdown/pdf/docx)
- `DELETE /api/reports/<id>` - Delete specific research report
- `GET /health` - API health check

## Database Management

```bash
# View database statistics
venv/bin/python manage_db.py --stats

# List recent reports
venv/bin/python manage_db.py --list

# Show specific report
venv/bin/python manage_db.py --show <research-id>

# Clean up old reports (30+ days)
venv/bin/python manage_db.py --cleanup 30
```

## CLI Usage

```bash
# Direct CLI usage
python deep_crawler/cli.py "your research question"

# Or use the virtual environment
venv/bin/python deep_crawler/cli.py "your research question"
```
