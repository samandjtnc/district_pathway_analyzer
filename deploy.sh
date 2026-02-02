#!/bin/bash
# Deployment script for District Pathway Analyzer

set -e

echo "🎓 District Pathway Analyzer - Deployment Script"
echo "================================================"

# Check for .env file
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo ""
    echo "Create a .env file with your Anthropic API key:"
    echo ""
    echo "  echo 'ANTHROPIC_API_KEY=your_key_here' > .env"
    echo ""
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   https://docs.docker.com/engine/install/"
    exit 1
fi

# Check if Docker Compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

echo ""
echo "📦 Building Docker image..."
$COMPOSE_CMD build

echo ""
echo "🚀 Starting the service..."
$COMPOSE_CMD up -d

echo ""
echo "✅ Deployment complete!"
echo ""
echo "   The service is running at: http://localhost:8000"
echo ""
echo "   View logs:     $COMPOSE_CMD logs -f"
echo "   Stop service:  $COMPOSE_CMD down"
echo "   Restart:       $COMPOSE_CMD restart"
echo ""
