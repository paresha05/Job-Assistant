#!/bin/bash
set -e

echo "🛠️  Starting Development Environment"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Creating .env from template..."
    cp .env.template .env
    echo "✏️  Please edit .env file and add your API keys, then run this script again."
    exit 1
fi

# Development mode with hot reload
echo "🔨 Building development image..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

echo "🚀 Starting development environment..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

echo "🎉 Development environment started!"
