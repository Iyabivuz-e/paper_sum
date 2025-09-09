# Dockerfile for AI Paper Summarizer Backend Production Deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including PostgreSQL development headers
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv

# Copy dependency files and README
COPY pyproject.toml uv.lock README.md ./

# Explicitly install psycopg2-binary first to avoid compilation issues
RUN uv pip install --system psycopg2-binary==2.9.10

# Install dependencies (no need for editable install in production)
RUN uv sync --no-dev --no-editable

# Copy application code - flatten app directory to avoid double nesting
COPY main.py start.sh ./
COPY app/api ./api
COPY app/core ./core  
COPY app/models ./models
COPY app/pipeline ./pipeline
COPY app/services ./services
COPY app/__init__.py app/utils.py ./
COPY prisma ./prisma

# Set Python path so imports work correctly
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Make startup script executable
RUN chmod +x start.sh

# Generate Prisma client
RUN uv run prisma generate

# Create required directories
RUN mkdir -p outputs research_papers db logs

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8001}/health || exit 1

# Run the application with startup script
CMD ["./start.sh"]
