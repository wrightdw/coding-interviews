#!/bin/bash

# Integration Test Runner
# This script runs the backend integration tests

set -e

echo "================================================"
echo "Running Integration Tests"
echo "================================================"
echo ""

cd "$(dirname "$0")"

echo "📦 Ensuring dependencies are installed..."
uv sync
echo ""

echo "🧪 Running integration tests..."
echo ""
uv run pytest tests/test_integration.py -v --tb=short

echo ""
echo "================================================"
echo "✅ Integration tests complete!"
echo "================================================"
