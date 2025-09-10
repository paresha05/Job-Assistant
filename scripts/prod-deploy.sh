#!/bin/bash
set -e

echo "🏭 Starting Production Deployment"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create a .env file with your API keys for production:"
    echo "  USAJOBS_API_KEY=your_production_key"
    echo "  GEMINI_API_KEY=your_production_key"
    exit 1
fi

# Validate environment variables
if ! grep -q "USAJOBS_API_KEY=.*[^[:space:]]" .env || ! grep -q "GEMINI_API_KEY=.*[^[:space:]]" .env; then
    echo "❌ API keys not properly configured in .env file"
    exit 1
fi

# Create necessary directories
echo "📁 Creating production directories..."
mkdir -p data/cover_letters
mkdir -p logs
mkdir -p ssl  # For SSL certificates

# Build production image
echo "🔨 Building production Docker image..."
docker-compose build --no-cache

# Start with nginx proxy
echo "🚀 Starting production environment with reverse proxy..."
docker-compose --profile production up -d

echo "⏳ Waiting for services to start..."
sleep 15

# Health check
echo "🔍 Checking application health..."
if curl -f http://localhost/health >/dev/null 2>&1; then
    echo "✅ Production deployment successful!"
    echo "🌐 Application available at: http://localhost"
    echo "🔒 For HTTPS, configure SSL certificates in the ssl/ directory"
else
    echo "❌ Production deployment failed"
    echo "📋 Check logs with: docker-compose --profile production logs"
    exit 1
fi

echo ""
echo "🎉 Production deployment completed!"
echo "📊 View logs: docker-compose --profile production logs -f"
echo "🛑 Stop services: docker-compose --profile production down"
echo "📊 Monitor: docker-compose --profile production ps"
