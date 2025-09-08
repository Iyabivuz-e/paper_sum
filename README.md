# LaughGraph: Serious + Human-Fun AI Research Digest

![Python](https://img.shields.io/badge/python## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key
- uv (recommended) or pipblue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-powered-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

> Making AI research papers both educational and fun — because who says science can't make you smile? 😊

## 🎯 Core Purpose

To help researchers, students, and curious readers understand AI research papers quickly — with clear explanations and light, witty humor that makes the insights stick.

## 🚀 The Problem

AI research papers are often:
- Dense and difficult to understand
- Repetitive with similar approaches
- Over-hyped with minimal actual novelty
- Boring for general audiences

Readers either struggle to understand them or get bored halfway through.

## 💡 The Solution

A **LangGraph-powered assistant** that produces two synchronized perspectives for each paper:

- **Serious summary** → accurate, structured explanation
- **Human-fun version** → light humor, analogies, and emojis that make it relatable

## 🔗 Why LangGraph?

- **Branching**: Supports serious vs fun processing paths
- **Conditions**: If novelty is low → add playful "same recipe" analogies
- **Feedback loops**: Fun side can ask serious side for clarity
- **Workflow orchestration**: Complex multi-step processing with decision points

## 🧩 MVP Pipeline Architecture

Your **5-Node LangGraph Pipeline**:

```mermaid
graph TD
    A[User Query + arXiv ID] --> B[Node 1: Get Paper from arXiv]
    B --> C[Node 2: Chunk & Embed to Vector DB]
    C --> D[Node 3: Serious Summary + Context]
    D --> E[Node 4: Human-Fun Translation]
    E --> F[Node 5: Synthesis & Output]
    F --> G[Multi-Format Results]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
    style F fill:#f1f8e9
    style G fill:#e0f2f1
```

### Pipeline Flow:

1. **📥 Input**: User provides arXiv ID or PDF URL
2. **🔍 Node 1**: Download & parse paper from arXiv → extract text
3. **🧩 Node 2**: Split into chunks → embed → store in Chroma vector DB
4. **🎯 Node 3**: RAG retrieval → serious summary + contextual analysis
5. **😄 Node 4**: Transform serious content → add humor, analogies, emojis
6. **🔗 Node 5**: Merge perspectives → generate digest, tweets, blog format

### State Management:

```python
PaperState = {
    "arxiv_id": "2310.06825",
    "paper_title": "...",
    "serious_summary": "...",
    "human_fun_summary": "...", 
    "final_digest": "...",
    "tweet_thread": [...],
    "blog_post": "..."
}
```

## 🌟 Key Features

- **Dual Perspective**: "What the paper says" + "How it feels in human language"
- **Gentle Humor**: No harsh roasts — just witty analogies and light jokes
- **Conditional Fun**: Humor depth adapts (low novelty → more playful analogies)
- **Trend Tracking**: Identifies repeated themes ("yet another fine-tune") 
- **Accessible Digest**: Makes research both educational and entertaining

## 🆚 What's Unique?

Other tools either:
- Summarize papers seriously (boring) 📚
- Make jokes without structure (unhelpful) 🃏

**LaughGraph** = Structured research analysis + human-fun commentary in one conditional workflow.

> Think of it as a study guide that explains papers clearly while also making you smile! 😄

## � Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- uv (recommended) or pip

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/laughgraph.git
cd laughgraph

# Install dependencies with uv
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key
```

### Run Your First Paper

```bash
# Interactive mode
python main.py

# Or directly in Python
from main import run_single_paper_pipeline
run_single_paper_pipeline("2310.06825")  # Any arXiv ID
```

### Expected Output

```
📄 PAPER TITLE: Your Paper Title Here

🎯 SERIOUS SUMMARY: 
Technical analysis with methodology, results, and significance...

😄 FUN SUMMARY:
Imagine if your AI model went to the gym and came back with bigger muscles! 💪
This paper basically teaches machines to lift heavier intellectual weights...

🔗 FINAL DIGEST:
A conversation between a professor and a friend about exciting research...

🐦 TWITTER THREAD:
1/ 🧵 New AI paper just dropped and it's actually pretty cool!
2/ The main idea: instead of training bigger models, make them smarter...
```

See **[QUICKSTART.md](QUICKSTART.md)** for detailed setup instructions.

## 🚀 Quick Start

```python
from arxiv_docs import ArxivAPI
from langraph_pipeline import LaughGraphPipeline

# Initialize the pipeline
pipeline = LaughGraphPipeline()

# Process a paper from ArXiv ID
result = pipeline.process_paper("2312.12345")

print("Serious Summary:")
print(result.serious_summary)

print("\nFun Version:")
print(result.fun_summary)
```

## 📁 Project Structure

```
paper_sum/
├── arxiv_docs/           # ArXiv API and PDF processing
│   ├── arxiv_api.py     # Fetch papers from ArXiv
│   └── clean_pdfs.py    # PDF parsing and chunking
├── db/                  # Vector database storage
│   └── chroma_store/    # Chroma embeddings
├── research_papers/     # Downloaded PDFs and extracted text
├── langraph_nodes/      # LangGraph workflow nodes
├── main.py             # Main application entry point
├── pyproject.toml      # Project dependencies
└── README.md           # This file
```

## 🔄 Workflow Examples

### Processing Pipeline

1. **Input**: ArXiv paper ID or PDF file
2. **Extraction**: Parse content and create chunks
3. **Analysis**: Generate serious technical summary
4. **Fun Generation**: Add humor and analogies
5. **Output**: Combined digest with both perspectives

### Sample Output

**Paper**: "Attention Is All You Need"

**Serious**: "The paper introduces the Transformer architecture, replacing recurrent layers with self-attention mechanisms for sequence-to-sequence tasks..."

**Fun**: "The authors basically said 'Who needs memory when you have really good focus?' and created a model that pays attention to everything at once. It's like having ADHD but in a productive way! 🧠✨"

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
uv sync --dev

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy .
```

## 📊 Roadmap

- [ ] **v1.0**: Basic ArXiv processing with dual summaries
- [ ] **v1.1**: Web interface for interactive paper exploration
- [ ] **v1.2**: Social media thread generation
- [ ] **v2.0**: Multi-language support
- [ ] **v2.1**: Audio summaries with different tones
- [ ] **v3.0**: Real-time paper trend analysis

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangGraph** team for the amazing workflow framework
- **ArXiv** for providing open access to research papers
- **Chroma** for vector database capabilities
- The research community for creating papers worth summarizing (and gently joking about)

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/laughgraph/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/laughgraph/discussions)
- **Email**: your.email@example.com

---

*"Making AI research accessible, one laugh at a time!"* 😄🔬
