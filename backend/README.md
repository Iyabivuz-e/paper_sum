# AI Paper Summarizer Backend

FastAPI backend for processing and summarizing research papers with AI-powered analysis.

## Features

- ArXiv paper processing
- AI-powered summarization with Groq LLM
- Vector database for context retrieval
- Multiple output formats (serious, fun, friend's take)

## Setup

```bash
uv sync
uv run uvicorn app.main:app --reload
```

## API Endpoints

- `POST /api/summarize` - Process and summarize a paper
- `GET /api/jobs/{job_id}` - Get job status and results
- `GET /health` - Health check
