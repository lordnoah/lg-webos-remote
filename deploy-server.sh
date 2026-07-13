#!/bin/bash
# Server-side deployment helper script
set -e

echo "=== Starting deployment on remote server ==="
echo "Pulling latest changes from GitHub..."
git pull origin master

echo "Rebuilding and restarting Docker container..."
sudo docker-compose up -d --build

echo "=== Deployment completed successfully! ==="
