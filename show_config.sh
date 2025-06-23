#!/bin/bash

echo "=== Deep Crawler Configuration Demo ==="
echo

echo "Current configuration:"
venv/bin/python -c "
import toml
config = toml.load('config.toml')
print(f'API Server: {config[\"server\"][\"api_host\"]}:{config[\"server\"][\"api_port\"]}')
print(f'UI Server: {config[\"server\"][\"ui_host\"]}:{config[\"server\"][\"ui_port\"]}')
print(f'API Backend: {config[\"server\"][\"api_backend\"]}')
"

echo
echo "To change ports, edit config.toml [server] section:"
echo "  api_port = 3001"
echo "  ui_port = 3000"
echo "  api_backend = \"http://127.0.0.1:3001\""
echo
echo "To change API backend for UI (e.g., remote server):"
echo "  api_backend = \"http://remote-server:3001\""
echo
echo "All services will use the unified configuration!"
