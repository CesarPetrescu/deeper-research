#!/bin/bash

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Deep Crawler AI Research System...${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "config.toml" ]; then
    echo -e "${RED}❌ Error: config.toml not found. Please run from the project root directory.${NC}"
    exit 1
fi

# Load configuration to get port numbers
API_PORT=$(grep -A 10 "\[server\]" config.toml | grep "api_port" | cut -d'=' -f2 | tr -d ' ')
UI_PORT=$(grep -A 10 "\[server\]" config.toml | grep "ui_port" | cut -d'=' -f2 | tr -d ' ')

# Set default ports if not found
API_PORT=${API_PORT:-5000}
UI_PORT=${UI_PORT:-3000}

echo -e "${YELLOW}📋 Configuration:${NC}"
echo -e "   • API Port: ${API_PORT}"
echo -e "   • UI Port: ${UI_PORT}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Error: Python virtual environment not found.${NC}"
    echo -e "${YELLOW}💡 Please run: python -m venv venv && venv/bin/pip install -r requirements.txt${NC}"
    exit 1
fi

# Check if UI dependencies are installed
if [ ! -d "ui/node_modules" ]; then
    echo -e "${YELLOW}⚠️ UI dependencies not found. Installing...${NC}"
    cd ui
    npm install
    cd ..
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Stopping services...${NC}"
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
        echo -e "${GREEN}✅ API server stopped${NC}"
    fi
    if [ ! -z "$UI_PID" ]; then
        kill $UI_PID 2>/dev/null
        echo -e "${GREEN}✅ UI server stopped${NC}"
    fi
    echo -e "${BLUE}👋 Deep Crawler services stopped.${NC}"
    exit 0
}

# Set up trap for cleanup
trap cleanup INT TERM

# Start Python API server
echo -e "${BLUE}🖥️ Starting Python API server on port ${API_PORT}...${NC}"
cd /root/deeperres
PYTHONPATH=. venv/bin/python deep_crawler/api_server.py > api_server.log 2>&1 &
API_PID=$!

# Check if API server started successfully
sleep 3
if ! kill -0 $API_PID 2>/dev/null; then
    echo -e "${RED}❌ Failed to start API server. Check api_server.log for details.${NC}"
    tail -10 api_server.log
    exit 1
fi

echo -e "${GREEN}✅ API server started successfully (PID: $API_PID)${NC}"

# Start UI server
echo -e "${BLUE}🌐 Starting UI server on port ${UI_PORT}...${NC}"
cd /root/deeperres/ui
npm start > ../ui_server.log 2>&1 &
UI_PID=$!

# Check if UI server started successfully
sleep 5
if ! kill -0 $UI_PID 2>/dev/null; then
    echo -e "${RED}❌ Failed to start UI server. Check ui_server.log for details.${NC}"
    tail -10 ../ui_server.log
    cleanup
    exit 1
fi

echo -e "${GREEN}✅ UI server started successfully (PID: $UI_PID)${NC}"
echo ""
echo -e "${GREEN}🎉 All services running successfully!${NC}"
echo ""
echo -e "${BLUE}📡 Service URLs:${NC}"
echo -e "   • ${GREEN}Deep Crawler API:${NC} http://localhost:${API_PORT}"
echo -e "   • ${GREEN}Web UI:${NC} http://localhost:${UI_PORT}"
echo ""
echo -e "${BLUE}📋 Service Status:${NC}"
echo -e "   • API Server PID: ${API_PID}"
echo -e "   • UI Server PID: ${UI_PID}"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo -e "   • View API logs: tail -f api_server.log"
echo -e "   • View UI logs: tail -f ui_server.log"
echo -e "   • Press Ctrl+C to stop all services"
echo ""
echo -e "${BLUE}🔄 Waiting for services... (Press Ctrl+C to stop)${NC}"

# Wait for interrupt
wait
