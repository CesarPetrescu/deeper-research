#!/bin/bash

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 Stopping Deep Crawler services...${NC}"

# Find and kill API server processes
API_PIDS=$(pgrep -f "deep_crawler/api_server.py")
if [ ! -z "$API_PIDS" ]; then
    echo -e "${YELLOW}🔍 Found API server processes: $API_PIDS${NC}"
    kill $API_PIDS
    echo -e "${GREEN}✅ API server stopped${NC}"
else
    echo -e "${YELLOW}⚠️ No API server processes found${NC}"
fi

# Find and kill UI server processes (Node.js)
UI_PIDS=$(pgrep -f "node.*server.js")
if [ ! -z "$UI_PIDS" ]; then
    echo -e "${YELLOW}🔍 Found UI server processes: $UI_PIDS${NC}"
    kill $UI_PIDS
    echo -e "${GREEN}✅ UI server stopped${NC}"
else
    echo -e "${YELLOW}⚠️ No UI server processes found${NC}"
fi

# Clean up log files if they exist
if [ -f "api_server.log" ]; then
    rm api_server.log
    echo -e "${GREEN}🧹 Cleaned up API server logs${NC}"
fi

if [ -f "ui_server.log" ]; then
    rm ui_server.log
    echo -e "${GREEN}🧹 Cleaned up UI server logs${NC}"
fi

echo -e "${BLUE}👋 All Deep Crawler services stopped.${NC}"
