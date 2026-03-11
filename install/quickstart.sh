#!/usr/bin/env bash

# Quick Start Script for Desktop Production Suite Installer
# This script sets up everything you need to get started

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CLI_MODE=false
SERVER_PORT="8887"

print_manual_port_release_instructions() {
    local port="$1"

    echo ""
    echo "✗ Port $port is still in use."
    echo "  The current environment could not stop the process automatically."
    echo "  Run this command in a regular terminal outside Agent CLI:"
    echo "  lsof -ti:$port | xargs kill -9"
    echo ""
    echo "Then run quickstart in a virtual environment:"
    echo "macOS/Linux:"
    echo "python3 -m venv env"
    echo "source env/bin/activate"
    echo "./desktop/install/quickstart.sh $port"
    echo ""
    echo "Windows:"
    echo "python -m venv env"
    echo "env\\Scripts\\activate"
    echo "./desktop/install/quickstart.sh $port"
}

# Parse args:
#   --cli / --automated
#   --port <num> or --port=<num>
#   <num> (positional port)
while [[ $# -gt 0 ]]; do
    case "$1" in
        --cli|--automated)
            CLI_MODE=true
            shift
            ;;
        --port)
            if [[ -z "$2" ]]; then
                echo "✗ Missing value for --port"
                exit 1
            fi
            SERVER_PORT="$2"
            shift 2
            ;;
        --port=*)
            SERVER_PORT="${1#--port=}"
            shift
            ;;
        *)
            if [[ "$1" =~ ^[0-9]+$ ]]; then
                SERVER_PORT="$1"
            fi
            shift
            ;;
    esac
done

if ! [[ "$SERVER_PORT" =~ ^[0-9]+$ ]]; then
    echo "✗ Invalid port: $SERVER_PORT"
    exit 1
fi

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   Desktop Production Suite Installer                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check Python
echo "🔍 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Found: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON=python
    PYTHON_VERSION=$(python --version)
    echo "✓ Found: $PYTHON_VERSION"
else
    echo "✗ Python not found!"
    echo "  Please install Python 3.6 or higher from:"
    echo "  https://www.python.org/downloads/"
    exit 1
fi

echo ""

# Check if .env exists
echo "🔍 Checking for API key configuration..."
ENV_PATH="../../docker/.env"
if [ -f "$ENV_PATH" ]; then
    if grep -q "ANTHROPIC_API_KEY=your_api_key_here" "$ENV_PATH" || \
       grep -q "ANTHROPIC_API_KEY=$" "$ENV_PATH"; then
        echo "⚠️  .env file found but API key not configured"
        echo "  Edit $ENV_PATH to add your Anthropic API key"
        echo "  (Optional: LLM features will be disabled without it)"
    else
        echo "✓ API key configured"
    fi
else
    echo "⚠️  No .env file found"
    if [ "$CLI_MODE" = false ]; then
        echo "  To enable LLM features:"
        echo "  1. Copy .env.example to ../../docker/.env"
        echo "  2. Add your Anthropic API key"
        echo ""
        echo "  Create .env now? (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            mkdir -p "../../docker"
            cp .env.example "$ENV_PATH"
            echo "✓ Created $ENV_PATH"
            echo "  Please edit it to add your API key"
        fi
    else
        # In CLI mode, create .env silently if .env.example exists
        if [ -f ".env.example" ]; then
            mkdir -p "../../docker"
            cp .env.example "$ENV_PATH"
            echo "  (Created $ENV_PATH from template - edit to add API key)"
        fi
    fi
fi

echo ""

# Check for anthropic package (optional)
echo "🔍 Checking for Anthropic Python package..."
if $PYTHON -c "import anthropic" 2>/dev/null; then
    echo "✓ Anthropic package installed"
else
    echo "⚠️  Anthropic package not installed"
    if [ "$CLI_MODE" = false ]; then
        echo "  Install it for LLM features: pip install anthropic"
        echo ""
        echo "  Install now? (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo "  Installing..."
            $PYTHON -m pip install anthropic --break-system-packages 2>/dev/null || \
            $PYTHON -m pip install anthropic
            echo "✓ Installed"
        fi
    else
        # In CLI mode, skip prompting - will be installed later in venv if API key is configured
        echo "  (Will install in virtual environment if API key is configured)"
    fi
fi

echo ""

# Make scripts executable
echo "🔧 Setting up scripts..."
chmod +x setup.sh server.py
echo "✓ Scripts are now executable"

echo ""

# Check desktop.conf
echo "📦 Checking app configuration..."
if [ ! -f "desktop.conf" ]; then
    echo "✗ desktop.conf not found!"
    exit 1
fi

ENABLED_COUNT=$(grep -v "^#" desktop.conf | grep -v "^$" | wc -l | tr -d ' ')
TOTAL_COUNT=$(grep -v "^$" desktop.conf | wc -l | tr -d ' ')

echo "✓ Found $TOTAL_COUNT apps ($ENABLED_COUNT enabled)"

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   Setup Complete!                                         ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "📚 Next Steps:"
echo ""
echo "1. Start the server:"
echo "   $PYTHON server.py --port $SERVER_PORT"
echo ""
echo "2. Open your browser to:"
echo "   http://localhost:$SERVER_PORT"
echo ""
echo "3. Or use the command line:"
echo "   ./setup.sh"
echo ""
echo "📖 Documentation:"
echo "   - README.md - Setup and Architecture overview"
echo "   - CLAUDE_VIBES.md - AI modification examples"
echo ""
echo "🎯 Quick Tips:"
echo "   - Edit desktop.conf to enable/disable apps"
echo "   - Use the web UI for visual app management"
echo "   - Use AI Assistant for custom modifications"
echo "   - Check the console for command examples"
echo ""
echo "🧪 Run quickstart in a virtual environment (from webroot):"
echo "macOS/Linux:"
echo "python3 -m venv env"
echo "source env/bin/activate"
echo "./desktop/install/quickstart.sh $SERVER_PORT"
echo ""
echo "Windows:"
echo "python -m venv env"
echo "env\\Scripts\\activate"
echo "./desktop/install/quickstart.sh $SERVER_PORT"
echo ""

# Skip Enter prompt if in CLI mode
if [ "$CLI_MODE" = false ]; then
    echo "Press Enter to start the server now, or Ctrl+C to exit..."
    read -r
fi

# Start server with virtual environment
echo ""
echo "🚀 Starting server with virtual environment..."
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "env" ]; then
    echo "Creating virtual environment..."
    $PYTHON -m venv env
fi

# Activate virtual environment
if [ -f "env/bin/activate" ]; then
    source env/bin/activate
elif [ -f "env/Scripts/activate" ]; then
    source env/Scripts/activate
fi

# Install anthropic package if needed and API key is configured
if [ -f "$ENV_PATH" ]; then
    if ! grep -q "ANTHROPIC_API_KEY=your_api_key_here" "$ENV_PATH" && \
       ! grep -q "ANTHROPIC_API_KEY=$" "$ENV_PATH"; then
        # API key is configured, ensure anthropic package is installed
        if ! $PYTHON -c "import anthropic" 2>/dev/null; then
            echo "Installing anthropic package for Claude API..."
            $PYTHON -m pip install anthropic --quiet
        fi
    fi
fi

# Stop any existing process bound to requested port
if lsof -ti:"$SERVER_PORT" >/dev/null 2>&1; then
    echo "⚠️  Port $SERVER_PORT is in use. Stopping existing process(es)..."
    lsof -ti:"$SERVER_PORT" | xargs kill -9 2>/dev/null || true
    sleep 1

    if lsof -ti:"$SERVER_PORT" >/dev/null 2>&1; then
        print_manual_port_release_instructions "$SERVER_PORT"
        exit 1
    fi
fi

# Start server
$PYTHON server.py --port "$SERVER_PORT" --no-port-shift
