#!/bin/bash
# Quick launcher for Broken Divinity
cd "$(dirname "$0")"
echo "🎮 Launching Broken Divinity..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    python -m src.main
else
    python -m src.main
fi
