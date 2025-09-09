#!/bin/bash
set -e

# Set Python path explicitly
export PYTHONPATH=/app

# Print environment for debugging
echo "PYTHONPATH: $PYTHONPATH"
echo "PWD: $(pwd)"
echo "Python version: $(python --version)"
echo "App structure:"
ls -la /app/ | head -15
echo "Modules available:"
ls -la /app/services/ /app/models/ /app/core/ 2>/dev/null || echo "Some modules missing"

# Run the application
exec uv run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001}
