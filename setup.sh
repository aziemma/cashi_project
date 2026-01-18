#!/bin/bash

# Cashi Credit Scoring - Setup Script

set -e

case "${1:-}" in
    start|"")
        mkdir -p data logs
        docker compose up -d --build
        echo ""
        echo "Cashi Credit Scoring is running!"
        echo ""
        echo "  Frontend: http://localhost:8501"
        echo "  Backend:  http://localhost:8000"
        echo "  API Docs: http://localhost:8000/docs"
        echo ""
        ;;
    stop)
        docker compose down
        echo "Services stopped."
        ;;
    logs)
        docker compose logs -f
        ;;
    clean)
        echo "Cleaning up containers, images, and volumes..."
        docker compose down --rmi all --volumes --remove-orphans
        echo "Cleanup complete."
        ;;
    *)
        echo "Usage: ./setup.sh [start|stop|logs|clean]"
        ;;
esac
