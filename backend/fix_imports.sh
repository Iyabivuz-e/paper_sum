#!/bin/bash
# Script to fix all app. imports to relative imports

# Files to fix
files=(
    "app/pipeline/nodes.py"
    "app/services/monitoring.py"
    "app/models/analytics.py"
    "app/pipeline/state.py"
    "app/services/pipeline_service.py"
    "app/core/database.py"
    "app/api/dependencies.py"
    "app/api/analytics.py"
)

for file in "${files[@]}"; do
    echo "Fixing imports in $file"
    sed -i 's/from app\.core\./from core./g' "$file"
    sed -i 's/from app\.models\./from models./g' "$file"
    sed -i 's/from app\.pipeline\./from pipeline./g' "$file"
    sed -i 's/from app\.services\./from services./g' "$file"
    sed -i 's/from app\.api\./from api./g' "$file"
done

echo "Import fixes applied!"
