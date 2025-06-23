#!/usr/bin/env python3
"""
Configuration management utility for Deep Crawler
"""
import toml
import argparse
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.toml"
UI_CONFIG_PATH = Path(__file__).parent / "ui" / "config.json"

def load_config():
    """Load the main configuration"""
    print(f"Loading config from: {CONFIG_PATH}")
    return toml.load(CONFIG_PATH)

def save_config(config):
    """Save the main configuration"""
    with open(CONFIG_PATH, 'w') as f:
        toml.dump(config, f)

def update_ui_config():
    """Update UI config based on main config"""
    config = load_config()
    
    ui_config = {
        "api": {
            "baseUrl": config["server"]["api_backend"],
            "endpoints": {
                "research": "/api/research",
                "download": "/api/download"
            }
        },
        "server": {
            "host": config["server"]["ui_host"],
            "port": config["server"]["ui_port"]
        }
    }
    
    print(f"Updating UI config at: {UI_CONFIG_PATH}")
    with open(UI_CONFIG_PATH, 'w') as f:
        json.dump(ui_config, f, indent=2)

def set_api_port(port):
    """Set the API server port"""
    config = load_config()
    config["server"]["api_port"] = port
    config["server"]["api_backend"] = f"http://127.0.0.1:{port}"
    save_config(config)
    update_ui_config()
    print(f"API port set to {port}")

def set_ui_port(port):
    """Set the UI server port"""
    config = load_config()
    config["server"]["ui_port"] = port
    save_config(config)
    update_ui_config()
    print(f"UI port set to {port}")

def set_api_backend(url):
    """Set the API backend URL for the UI"""
    config = load_config()
    config["server"]["api_backend"] = url
    save_config(config)
    update_ui_config()
    print(f"API backend set to {url}")

def show_config():
    """Display current configuration"""
    config = load_config()
    print("Current Configuration:")
    print("=" * 50)
    print(f"API Server: {config['server']['api_host']}:{config['server']['api_port']}")
    print(f"UI Server: {config['server']['ui_host']}:{config['server']['ui_port']}")
    print(f"API Backend: {config['server']['api_backend']}")
    print(f"LLM Model: {config['api']['chat_model']}")
    print(f"Embedding Model: {config['api']['embed_model']}")
    print(f"Search Engine: {config['search']['searx_url']}")

def main():
    parser = argparse.ArgumentParser(description='Manage Deep Crawler configuration')
    parser.add_argument('--show', action='store_true', help='Show current configuration')
    parser.add_argument('--api-port', type=int, help='Set API server port')
    parser.add_argument('--ui-port', type=int, help='Set UI server port')
    parser.add_argument('--api-backend', help='Set API backend URL for UI')
    parser.add_argument('--update-ui', action='store_true', help='Update UI config from main config')
    
    args = parser.parse_args()
    
    if args.show:
        show_config()
    elif args.api_port:
        set_api_port(args.api_port)
    elif args.ui_port:
        set_ui_port(args.ui_port)
    elif args.api_backend:
        set_api_backend(args.api_backend)
    elif args.update_ui:
        update_ui_config()
        print("UI configuration updated")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
