# LaughGraph Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### 1. Installation

```bash
# Clone and setup
git clone <your-repo>
cd paper_sum

# Install dependencies (requires Python 3.9+)
uv sync
# or
pip install -e .
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

**Required API Keys:**
- `OPENAI_API_KEY` - Get from OpenAI dashboard
- `GROQ_API_KEY` - (Optional) Alternative LLM provider

### 3. Run Your First Paper

**Option A: CLI (Recommended for testing)**
```bash
# Interactive mode
python main.py interactive

# Direct processing
python main.py process --arxiv-id "2310.06825"
```

**Option B: API (Production mode)**
```bash
# Start API server
python main.py api
# Visit http://localhost:8000/docs for API documentation

# Process via API
curl -X POST "http://localhost:8000/papers/process" \
  -H "Content-Type: application/json" \
  -d '{"arxiv_id": "2310.06825"}'
```

**Option C: Python import (for scripts)**
```python
import asyncio
from main import run_single_paper_pipeline

# Process a paper by arXiv ID
result = asyncio.run(run_single_paper_pipeline("2310.06825"))
```

### 4. Choose Your Interface

**Interactive CLI:**
```bash
python main.py interactive
```

**API Server:**
```bash
python main.py api
# Then visit: http://localhost:8000/docs
```

**Legacy Batch Mode:**
```bash
python main.py batch
```

## 📋 Production Pipeline Flow

**New 7-Node Architecture:**
```
User Input (arXiv ID)
   ↓
Node 1: Ingestion (Download & Initial Processing)
   ↓ 
Node 2: Parsing (PDF Text Extraction)
   ↓
Node 3: RAG (Chunk, Embed, Store in Vector DB)
   ↓
Node 4: Summarizer + Context (Technical Analysis)
   ↓
Node 5: Novelty Analysis (Innovation Assessment)
   ↓
Node 6: Human-Fun Translation (Accessible Humor)
   ↓
Node 7: Output Generation (Multi-format Synthesis)
   ↓
Results (JSON, Markdown, Tweets, Blog)
```

## 🔧 Core Components

**Production Architecture:**
- **`app/main.py`** - FastAPI application with all endpoints
- **`app/pipeline/nodes.py`** - 7-node LangGraph pipeline
- **`app/pipeline/state.py`** - State management for pipeline
- **`app/services/pipeline_service.py`** - Business logic service
- **`app/core/config.py`** - Production configuration
- **`main.py`** - Enhanced CLI with backward compatibility
- **`arxiv_docs/`** - Legacy PDF processing (kept for compatibility)

**API Endpoints:**
- `POST /papers/process` - Process single paper
- `POST /papers/batch` - Process multiple papers  
- `GET /jobs/{job_id}` - Get job status & results
- `GET /health` - Health check
- `GET /metrics` - System metrics

## 📊 Expected Output

For each paper you'll get:
- **Serious Summary** - Technical, academic analysis
- **Contextual Analysis** - How it fits in the research landscape  
- **Novelty Score** - Innovation assessment (0-1 scale)
- **Human-Fun Summary** - Accessible explanation with analogies and humor
- **Final Digest** - Blended serious + fun perspective
- **Tweet Thread** - Social media ready content
- **Blog Post** - Long-form structured article

**Output Formats Available:**
- JSON (programmatic access)
- Markdown (documentation)
- Plain text (digest only)
- API responses (structured data)

## 🎯 Example arXiv IDs to Try

- `2310.06825` - Recent LLM paper
- `1706.03762` - "Attention Is All You Need" (Transformers)
- `2005.14165` - GPT-3 paper
- `2212.10560` - ChatGPT technical report

## 🐛 Troubleshooting

**Import Errors?**
```bash
uv sync  # Reinstall dependencies
```

**API Key Issues?**
```bash
echo $OPENAI_API_KEY  # Check if set
```

**Vector DB Issues?**
```bash
rm -rf db/chroma_store  # Reset database
```

## 📝 Next Steps

1. **Test with CLI** - Start with `python main.py interactive`
2. **Try the API** - Run `python main.py api` and visit `/docs`
3. **Check outputs folder** - Review generated JSON files
4. **Customize prompts** - Edit prompts in `app/pipeline/nodes.py`
5. **Deploy with Docker** - Use `docker-compose up -d`
6. **Scale for production** - Configure Redis, monitoring, etc.

**Production Deployment:**
```bash
# Build and run with Docker
docker-compose up -d

# Check logs
docker-compose logs -f laughgraph-api

# Scale workers
docker-compose up -d --scale laughgraph-api=3
```

Happy paper processing! 🎭📚
