#!/bin/bash

# FastAPI Backend Setup and Test Script

echo "========================================="
echo "FastAPI Backend - Setup and Test"
echo "========================================="
echo ""

cd "$(dirname "$0")"

# Install dependencies
echo "📦 Installing dependencies with uv..."
uv sync
echo "✅ Dependencies installed"
echo ""

# Run tests
echo "🧪 Running tests..."
uv run pytest -v --tb=short
TEST_EXIT_CODE=$?
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed (exit code: $TEST_EXIT_CODE)"
    exit $TEST_EXIT_CODE
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To start the server:"
echo "  cd server"
echo "  uv run python run.py"
echo ""
echo "API will be available at:"
echo "  http://localhost:3000"
echo "  http://localhost:3000/docs (Swagger UI)"
echo ""
