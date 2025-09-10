#!/bin/bash
set -e

echo "🚀 Starting Job Hunt Assistant Docker Deployment"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create a .env file with your API keys:"
    echo "  USAJOBS_API_KEY=your_key_here"
    echo "  GEMINI_API_KEY=your_key_here"
    echo ""
    echo "You can copy .env.template to .env and fill in your keys."
    exit 1
fi

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/cover_letters
mkdir -p logs

# Build and start the application
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting application..."
docker-compose up -d

echo "⏳ Waiting for application to start..."
sleep 10

# Check if the application is running
echo "🔍 Checking application status..."
if curl -f http://localhost:8501/_stcore/health >/dev/null 2>&1; then
    echo "✅ Application is running successfully!"
    echo "🌐 Access the application at: http://localhost:8501"
else
    echo "❌ Application failed to start properly"
    echo "📋 Check logs with: docker-compose logs"
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo "📊 View logs: docker-compose logs -f"
echo "🛑 Stop application: docker-compose down"
echo "🔄 Restart application: docker-compose restart"
