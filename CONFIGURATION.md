# Configuration Guide

Deep Crawler now uses a unified configuration system with a single `config.toml` file in the root directory and an auto-generated `ui/config.json` for the frontend.

## Main Configuration (`config.toml`)

The main configuration file contains all settings for the Deep Crawler system:

### API Settings
```toml
[api]
openai_base   = "http://192.168.100.199:5515/v1"    # Your LLM API endpoint
openai_key    = "none"                              # API key (if required)
chat_model    = "mistral-small-3.2-24b-instruct-2506"  # Chat model name
embed_model   = "text-embedding-granite-embedding-278m-multilingual"  # Embedding model
```

### Firecrawl Settings
```toml
[firecrawl]
base_url      = "http://localhost:3002"             # Firecrawl server URL
concurrency   = 8                                   # Async task concurrency
limit_per_url = 8                                   # Pages to crawl per seed URL
```

### Search Settings
```toml
[search]
searx_url         = "https://searx.sprk.ro/search"  # SearX search engine URL
urls_per_keyword  = 4                               # URLs to fetch per keyword
```

### Indexing Settings
```toml
[index]
snippets_per_sec  = 8                               # Snippets to process per section
```

### Server Settings
```toml
[server]
api_host     = "0.0.0.0"                           # API server bind address
api_port     = 3001                                 # API server port
ui_host      = "0.0.0.0"                           # UI server bind address  
ui_port      = 3000                                 # UI server port
api_backend  = "http://127.0.0.1:3001"             # API backend URL for UI
```

## UI Configuration (`ui/config.json`)

The UI configuration is automatically generated from the main config:

```json
{
  "api": {
    "baseUrl": "http://127.0.0.1:3001",
    "endpoints": {
      "research": "/api/research",
      "download": "/api/download"
    }
  },
  "server": {
    "host": "0.0.0.0",
    "port": 3000
  }
}
```

## Configuration Management

### View Current Configuration
```bash
./show_config.sh
```

### Change Ports
Edit `config.toml` and modify the `[server]` section:
```toml
[server]
api_port = 4001  # Change API port
ui_port = 4000   # Change UI port
```

### Use Remote API Backend
To connect the UI to a remote API server:
```toml
[server]
api_backend = "http://remote-server.example.com:3001"
```

### Environment-Specific Configurations

You can maintain different config files for different environments:

```bash
# Development
cp config.toml config.dev.toml

# Production  
cp config.toml config.prod.toml

# Use specific config
cp config.prod.toml config.toml
./start_services.sh
```

## Automatic Configuration Sync

The UI configuration is automatically synchronized with the main configuration:
- When you change `api_backend` in `config.toml`, the UI will use that endpoint
- Port changes are reflected in both API and UI servers
- No need to manually edit multiple config files

## Migration from Old Configuration

If you have an old setup with separate config files:
1. Merge all settings into the root `config.toml`
2. Remove `deep_crawler/config.toml` (no longer needed)
3. The UI config will be auto-generated on startup

This unified approach ensures consistency across all components and makes deployment much simpler!
