#!/bin/bash
# Test and Run workflow for Broken Divinity
# Runs tests first, only launches game if all tests pass

cd "$(dirname "$0")"

echo "🧪 Running Broken Divinity Test Suite..."
echo "========================================"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the test suite
python -m pytest -v

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed! Launching game..."
    echo "========================================"
    echo ""
    
    # Launch the game
    python -m src.main
else
    echo ""
    echo "❌ Tests failed! Fix tests before running game."
    echo "==============================================="
    exit 1
fi
