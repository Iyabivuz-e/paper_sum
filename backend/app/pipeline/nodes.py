"""
Production Pipeline: Ingestion → Parsing → RAG → Summarizer+Context → Novelty → Fun → Output
"""

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from pathlib import Path
import arxiv
import fitz
import re
from typing import Dict, Any, List, Optional
import structlog
import asyncio
from datetime import datetime

from core.config import settings
from models.schemas import ProcessingStatus, PaperProcessResponse, ProcessingStep
from pipeline.state import PipelineState

logger = structlog.get_logger()


class ProductionPipelineNodes:
    """Production-grade pipeline nodes with proper error handling and monitoring"""
    
    def __init__(self):
        # Initialize LLM with the specific Groq model requested by user
        if not settings.groq_api_key:
            raise ValueError("Groq API key is required for the requested model")
        
        try:
            # Use only the specific Groq model: openai/gpt-oss-20b
            self.llm = ChatGroq(
                model="openai/gpt-oss-120b",
                api_key=settings.groq_api_key,
                temperature=0.7
            )
            logger.info("Using Groq LLM: openai/gpt-oss-20b")
        except Exception as e:
            logger.error(f"Failed to initialize Groq model openai/gpt-oss-20b: {e}")
            raise e
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model
        )
        
        self.vector_store = Chroma(
            collection_name=settings.collection_name,
            embedding_function=self.embeddings,
            persist_directory=settings.chroma_persist_dir
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )

    async def _log_step_start(self, state: PipelineState, step_name: str) -> None:
        """Log step start and update state"""
        logger.info(f"Starting step: {step_name}", job_id=state["job_id"])
        
        step = ProcessingStep(
            step_name=step_name,
            status=ProcessingStatus.INGESTING,
            started_at=datetime.utcnow()
        )
        state["processing_steps"].append(step)
        state["current_step"] = step_name

    async def _log_step_complete(self, state: PipelineState, step_name: str) -> None:
        """Log step completion and update state"""
        logger.info(f"Completed step: {step_name}", job_id=state["job_id"])
        
        # Update the last step
        if state["processing_steps"]:
            last_step = state["processing_steps"][-1]
            if last_step.step_name == step_name:
                last_step.completed_at = datetime.utcnow()
                last_step.status = ProcessingStatus.COMPLETED
                if last_step.started_at:
                    duration = (last_step.completed_at - last_step.started_at).total_seconds()
                    last_step.duration_seconds = duration

    async def _log_step_error(self, state: PipelineState, step_name: str, error: str) -> None:
        """Log step error and update state"""
        logger.error(f"Error in step: {step_name}", error=error, job_id=state["job_id"])
        
        if state["processing_steps"]:
            last_step = state["processing_steps"][-1]
            if last_step.step_name == step_name:
                last_step.status = ProcessingStatus.FAILED
                last_step.error_message = error
                last_step.completed_at = datetime.utcnow()

    async def node_1_ingestion(self, state: PipelineState) -> PipelineState:
        """Node 1: Ingestion - Download and initial processing"""
        step_name = "ingestion"
        await self._log_step_start(state, step_name)
        
        try:
            if state["arxiv_id"]:
                # Fetch from arXiv
                client = arxiv.Client()
                search = arxiv.Search(id_list=[state["arxiv_id"]])
                paper = next(client.results(search))
                
                # Extract metadata
                state["paper_metadata"] = {
                    "title": paper.title,
                    "authors": [author.name for author in paper.authors],
                    "abstract": paper.summary,
                    "published_date": paper.published.isoformat(),
                    "arxiv_id": paper.entry_id,
                    "categories": [cat for cat in paper.categories]
                }
                
                # Download PDF
                pdf_path = Path(settings.research_papers_dir) / f"{state['job_id']}.pdf"
                pdf_path.parent.mkdir(exist_ok=True)
                paper.download_pdf(filename=str(pdf_path))
                state["pdf_path"] = str(pdf_path)
                
            elif state["pdf_file_path"]:
                # Handle uploaded PDF file
                pdf_path = state["pdf_file_path"]
                
                # Check if the file exists
                if not Path(pdf_path).exists():
                    raise FileNotFoundError(f"Uploaded PDF file not found: {pdf_path}")
                
                # Copy to the standard location
                standard_pdf_path = Path(settings.research_papers_dir) / f"{state['job_id']}.pdf"
                standard_pdf_path.parent.mkdir(exist_ok=True)
                
                import shutil
                shutil.copy2(pdf_path, standard_pdf_path)
                state["pdf_path"] = str(standard_pdf_path)
                
                # For uploaded PDFs, we create minimal metadata
                filename = Path(pdf_path).name
                state["paper_metadata"] = {
                    "title": filename.replace('.pdf', '').replace('_', ' ').title(),
                    "authors": ["Unknown"],
                    "abstract": "Abstract not available for uploaded PDF",
                    "published_date": "Unknown",
                    "arxiv_id": filename,  # Use filename as identifier
                    "categories": ["Uploaded PDF"]
                }
                
                # Clean up the temporary file
                try:
                    Path(pdf_path).unlink()
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file {pdf_path}: {e}")
                
            elif state["pdf_url"]:
                # Handle direct PDF URL - download the PDF
                import httpx
                from urllib.parse import urlparse
                
                pdf_url = state["pdf_url"]
                
                # Check if it's an ArXiv PDF URL and extract the ID
                arxiv_pdf_match = re.match(r'(?:https?://)?(?:www\.)?arxiv\.org/pdf/(\d{4}\.\d{4,5})(?:\.pdf)?', pdf_url)
                if arxiv_pdf_match:
                    # It's an ArXiv PDF URL, extract the ID and process as ArXiv paper
                    arxiv_id = arxiv_pdf_match.group(1)
                    state["arxiv_id"] = arxiv_id
                    state["pdf_url"] = None  # Clear pdf_url to avoid confusion
                    
                    # Fetch from arXiv
                    client = arxiv.Client()
                    search = arxiv.Search(id_list=[arxiv_id])
                    paper = next(client.results(search))
                    
                    # Extract metadata
                    state["paper_metadata"] = {
                        "title": paper.title,
                        "authors": [author.name for author in paper.authors],
                        "abstract": paper.summary,
                        "published_date": paper.published.isoformat(),
                        "arxiv_id": paper.entry_id,
                        "categories": [cat for cat in paper.categories]
                    }
                    
                    # Download PDF
                    pdf_path = Path(settings.research_papers_dir) / f"{state['job_id']}.pdf"
                    pdf_path.parent.mkdir(exist_ok=True)
                    paper.download_pdf(filename=str(pdf_path))
                    state["pdf_path"] = str(pdf_path)
                else:
                    # It's a non-ArXiv PDF URL, download directly
                    async with httpx.AsyncClient() as client:
                        response = await client.get(pdf_url)
                        response.raise_for_status()
                        
                        # Save PDF
                        pdf_path = Path(settings.research_papers_dir) / f"{state['job_id']}.pdf"
                        pdf_path.parent.mkdir(exist_ok=True)
                        
                        with open(pdf_path, 'wb') as f:
                            f.write(response.content)
                        
                        state["pdf_path"] = str(pdf_path)
                        
                        # For non-ArXiv PDFs, we can't get metadata from ArXiv
                        # We'll extract basic info during parsing or leave it minimal
                        parsed_url = urlparse(pdf_url)
                        filename = parsed_url.path.split('/')[-1] or "unknown.pdf"
                        
                        state["paper_metadata"] = {
                            "title": filename.replace('.pdf', '').replace('_', ' ').title(),
                            "authors": ["Unknown"],
                            "abstract": "Abstract not available for external PDF",
                            "published_date": "Unknown",
                            "arxiv_id": pdf_url,  # Use the URL as identifier
                            "categories": ["External PDF"]
                        }
                
            state["status"] = ProcessingStatus.PARSING
            await self._log_step_complete(state, step_name)
            
        except Exception as e:
            error_msg = f"Ingestion failed: {str(e)}"
            state["error_message"] = error_msg
            state["status"] = ProcessingStatus.FAILED
            await self._log_step_error(state, step_name, error_msg)
            
        return state

    async def node_2_parsing(self, state: PipelineState) -> PipelineState:
        """Node 2: Parsing - Extract and clean text from PDF"""
        step_name = "parsing"
        await self._log_step_start(state, step_name)
        
        try:
            if not state["pdf_path"]:
                raise ValueError("No PDF path available for parsing")
                
            # Extract text from PDF
            doc = fitz.open(state["pdf_path"])
            content = ""
            
            for page_num, page in enumerate(doc):
                blocks = page.get_text("blocks")
                # Sort blocks by vertical position for reading order
                blocks.sort(key=lambda b: b[1])
                for block in blocks:
                    content += block[4] + "\n"
            
            doc.close()
            
            # Clean and store content
            state["paper_content"] = content.strip()
            state["status"] = ProcessingStatus.RAG_PROCESSING
            await self._log_step_complete(state, step_name)
            
        except Exception as e:
            error_msg = f"Parsing failed: {str(e)}"
            state["error_message"] = error_msg
            state["status"] = ProcessingStatus.FAILED
            await self._log_step_error(state, step_name, error_msg)
            
        return state

    async def node_3_rag(self, state: PipelineState) -> PipelineState:
        """Node 3: RAG - Chunk, embed, and store in vector database"""
        step_name = "rag_processing"
        await self._log_step_start(state, step_name)
        
        try:
            if not state["paper_content"]:
                raise ValueError("No paper content available for RAG processing")
                
            # Filter complex metadata for ChromaDB (lists, dicts not allowed)
            simple_metadata = {}
            if state["paper_metadata"]:
                for key, value in state["paper_metadata"].items():
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        simple_metadata[key] = value
                    elif isinstance(value, list):
                        # Convert lists to comma-separated strings
                        simple_metadata[key] = ", ".join(str(item) for item in value)
                    else:
                        # Convert other types to string
                        simple_metadata[key] = str(value)
                
            # Create document
            document = Document(
                page_content=state["paper_content"],
                metadata=simple_metadata
            )
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([document])
            
            # Store in vector database
            chunk_ids = self.vector_store.add_documents(chunks)
            
            # Store chunk information
            state["text_chunks"] = [chunk.page_content for chunk in chunks]
            state["chunk_ids"] = chunk_ids
            
            # Retrieve relevant context for processing
            title = state["paper_metadata"].get('title', '')
            abstract = state["paper_metadata"].get('abstract', '')
            query = f"{title} {abstract}"
            retrieved_docs = self.vector_store.similarity_search(query, k=5)
            state["retrieved_context"] = [doc.page_content for doc in retrieved_docs]
            
            state["status"] = ProcessingStatus.SUMMARIZING
            await self._log_step_complete(state, step_name)
            
        except Exception as e:
            error_msg = f"RAG processing failed: {str(e)}"
            state["error_message"] = error_msg
            state["status"] = ProcessingStatus.FAILED
            await self._log_step_error(state, step_name, error_msg)
            
        return state

    async def node_4_summarizer_context(self, state: PipelineState) -> PipelineState:
        """Node 4: Summarizer + Context - Generate serious summary and contextual analysis"""
        step_name = "summarizer_context"
        await self._log_step_start(state, step_name)
        
        try:
            title = state["paper_metadata"].get("title", "")
            abstract = state["paper_metadata"].get("abstract", "")
            context = "\n".join(state["retrieved_context"][:3])  # Use top 3 chunks
            
            # Serious summarizer prompt
            serious_prompt = ChatPromptTemplate.from_template("""
            You are a senior AI researcher. Provide a concise, technical summary of this research paper.

            Paper Title: {title}
            Abstract: {abstract}
            Context: {context}

            Provide a structured analysis covering:
            1. Main contribution and significance (2-3 sentences)
            2. Technical approach (2-3 sentences) 
            3. Key results (1-2 sentences)
            4. Limitations (1-2 sentences)

            Be precise, technical, and objective. Keep it concise for busy researchers.
            Output should be 150-200 words maximum.
            """)
            
            # Contextualizer prompt
            context_prompt = ChatPromptTemplate.from_template("""
            You are an AI research expert. Explain how this paper fits into the broader AI research landscape.

            Paper Title: {title}
            Technical Summary: {summary}

            Provide contextual analysis covering:
            1. Historical context - what previous work this builds upon
            2. Research field positioning - what subfield/domain this belongs to
            3. Current relevance - why this work matters in today's research landscape
            4. Impact potential - how this might influence future research directions
            5. Comparison with similar approaches or competing methods
            6. Broader implications for the field

            Be insightful about research trends and provide scholarly perspective.
            Output should be 200-300 words.
            """)
            
            # Generate serious summary
            serious_chain = serious_prompt | self.llm
            serious_response = await serious_chain.ainvoke({
                "title": title,
                "abstract": abstract,
                "context": context
            })
            
            state["serious_summary"] = serious_response.content
            
            # Generate contextual analysis
            context_chain = context_prompt | self.llm
            context_response = await context_chain.ainvoke({
                "title": title,
                "summary": serious_response.content
            })
            
            state["contextual_analysis"] = context_response.content
            state["status"] = ProcessingStatus.NOVELTY_ANALYSIS
            await self._log_step_complete(state, step_name)
            
        except Exception as e:
            error_msg = f"Summarization failed: {str(e)}"
            state["error_message"] = error_msg
            state["status"] = ProcessingStatus.FAILED
            await self._log_step_error(state, step_name, error_msg)
            
        return state

    async def node_5_novelty(self, state: PipelineState) -> PipelineState:
        """Node 5: Novelty Analysis - Assess innovation and originality"""
        step_name = "novelty_analysis"
        await self._log_step_start(state, step_name)
        
        try:
            novelty_prompt = ChatPromptTemplate.from_template("""
            You are an AI research evaluation expert. Assess the novelty and innovation of this research paper.

            Paper Title: {title}
            Technical Summary: {summary}
            Context Analysis: {context}

            Evaluate the novelty across these dimensions:
            1. Methodological Innovation (0-1): How novel is the technical approach?
            2. Problem Formulation (0-1): How original is the problem being solved?
            3. Experimental Design (0-1): How innovative is the evaluation methodology?
            4. Theoretical Contribution (0-1): How much new theoretical insight is provided?
            5. Practical Impact (0-1): How novel are the practical applications/implications?

            Provide:
            1. Individual scores for each dimension (0.0 to 1.0)
            2. Overall novelty score (0.0 to 1.0)
            3. Brief justification for the scores
            4. Comparison with typical papers in this field

            Be objective and consider: Is this incremental improvement, significant advancement, or breakthrough?

            Format your response as:
            Methodological Innovation: X.X
            Problem Formulation: X.X
            Experimental Design: X.X
            Theoretical Contribution: X.X
            Practical Impact: X.X
            Overall Novelty Score: X.X

            Justification: [explanation]
            """)
            
            novelty_chain = novelty_prompt | self.llm
            novelty_response = await novelty_chain.ainvoke({
                "title": state["paper_metadata"].get("title", ""),
                "summary": state["serious_summary"],
                "context": state["contextual_analysis"]
            })
            
            # Extract novelty score (simple parsing - could be more sophisticated)
            novelty_text = novelty_response.content
            try:
                # Look for "Overall Novelty Score: X.X" pattern
                import re
                match = re.search(r"Overall Novelty Score:\s*(\d+\.?\d*)", novelty_text)
                if match:
                    state["novelty_score"] = float(match.group(1))
                else:
                    # Fallback: count novelty keywords
                    novelty_keywords = ["novel", "new", "first", "breakthrough", "unprecedented", "innovative"]
                    score = sum(1 for word in novelty_keywords 
                              if word.lower() in state["serious_summary"].lower()) / 10.0
                    state["novelty_score"] = min(score, 1.0)
            except:
                state["novelty_score"] = 0.5  # Default if parsing fails
            
            state["novelty_analysis"] = novelty_text
            state["status"] = ProcessingStatus.HUMANIZING
            await self._log_step_complete(state, step_name)
            
        except Exception as e:
            error_msg = f"Novelty analysis failed: {str(e)}"
            state["error_message"] = error_msg
            state["status"] = ProcessingStatus.FAILED
            await self._log_step_error(state, step_name, error_msg)
            
        return state

    async def node_6_fun(self, state: PipelineState) -> PipelineState:
        """Node 6: Human-Fun Translation - Make it accessible and entertaining with new format"""
        step_name = "humanizing"
        await self._log_step_start(state, step_name)
        
        try:
            fun_prompt = ChatPromptTemplate.from_template("""
                You are a brilliant science communicator who makes AI research accessible, fun, and easy to understand! 
                Your tone is like a friendly friend explaining tech over coffee — clear, playful, and relatable.

                Paper Title: {title}
                Serious Summary: {serious_summary}
                Novelty Score: {novelty_score}/1.0
                User Query: {user_query}

                Your mission:
                - Break down the research in a way that is:
                1. **Clear:** short plain-English explanation of each key point.
                2. **Fun:** add a simple analogy or metaphor (cooking, sports, everyday life).
                3. **Friendly Reaction:** add a playful side-joke, amazed remark, or relatable quip.
                - Use easy English — avoid heavy jargon.
                - Include emojis to enhance engagement.
                - Make sure humor helps with understanding, not just decoration.
                - Limit to 3–5 main points so it’s digestible.

                Adaptation based on novelty:
                - If novelty < 0.3: Add a gentle roast, like "Another day, another fine-tune 🔄... but hey, every pizza needs its toppings!"
                - If novelty 0.3–0.7: Be supportive but playful, e.g. "Pretty cool! Like upgrading from a bicycle to a motorcycle 🏍️."
                - If novelty > 0.7: Sound genuinely excited, e.g. "WHOA! 🤯 This is like discovering fire but for AI!"

                Style guidelines:
                - Friendly, witty, conversational — think "Science YouTube explainer meets fun Twitter thread".
                - Respectful (no harsh criticism).
                - Length: 250–400 words.

                Output format:
                For each key point:
                **Serious:** ...
                **Fun:** ...

                ### EXAMPLES ###

                Example 1:
                **Serious:** "Grouped Query Attention reduces redundant computations by letting multiple queries share the same key/value."
                **Fun:** "Think of it like students sharing the same class notes 📚 — way faster than each one rewriting the whole book. And honestly, you know that one kid who never brings a pen? Yeah, GQA is saving *that* kid every single day 😂."

                Example 2:
                **Serious:** "Sliding Window Attention allows the model to handle long texts (32k tokens) efficiently."
                **Fun:** "It’s like peeking through blinds instead of tearing down the whole wall 🏠👀. Efficient, focused… and way less likely to get you grounded by your parents 😅."

                Now, generate the output in the same format and style.
                """)

            
            fun_chain = fun_prompt | self.llm
            fun_response = await fun_chain.ainvoke({
                "title": state["paper_metadata"].get("title", ""),
                "serious_summary": state["serious_summary"],
                "novelty_score": state["novelty_score"],
                "user_query": state["user_query"] or "general explanation"
            })
            
            state["human_fun_summary"] = fun_response.content
            state["status"] = ProcessingStatus.SYNTHESIZING
            await self._log_step_complete(state, step_name)
            
        except Exception as e:
            error_msg = f"Fun translation failed: {str(e)}"
            state["error_message"] = error_msg
            state["status"] = ProcessingStatus.FAILED
            await self._log_step_error(state, step_name, error_msg)
            
        return state

    async def node_7_output(self, state: PipelineState) -> PipelineState:
        """Node 7: Output Generation - Create final synthesis and multiple formats"""
        step_name = "output_generation"
        await self._log_step_start(state, step_name)
        
        try:
            synthesis_prompt = ChatPromptTemplate.from_template("""
            You are a master content synthesizer. Create multiple formats from this research analysis.

            Title: {title}
            Serious Analysis: {serious_summary}
            Context: {contextual_analysis}
            Novelty Analysis: {novelty_analysis}
            Fun Perspective: {human_fun_summary}
            
            CREATE THREE OUTPUTS:

            1. FRIEND'S TAKE - COFFEE CHAT CONVERSATION (≈350 words):
            Format as a conversation between a Professor and a Friend discussing the paper over coffee.
            
            **Professor:** "So, what's the big deal with [Paper Title]?"
            **Friend:** [Curious question about the topic]
            **Professor:** [Technical explanation with accessible language]
            **Friend:** [Follow-up question or concern]
            **Professor:** [More detailed explanation with examples]
            **Friend:** [Question about results/impact]
            **Professor:** [Results and significance]
            **Friend:** [Final question about limitations or future]
            **Professor:** [Wrap-up with broader implications]
            
            Make it natural, informative, and engaging. The Professor should be knowledgeable but accessible, the Friend should ask smart questions a curious person would ask.

            2. TWITTER THREAD (5-6 tweets):
            Format as:
            1/🧵 [Hook with key insight]
            2/🧵 [Main innovation with analogy]
            3/🧵 [Results/impact + numbers]
            4/🧵 [Why it matters today]
            5/🧵 [Future implications]
            6/🧵 [Conclusion + paper link]

            3. BLOG POST STRUCTURE:
            # {title}
            ## TL;DR
            ## The Problem
            ## The Approach
            ## Key Findings
            ## Why This Matters
            ## Looking Forward
            
            Make each format standalone but complementary.
            """)
            
            synthesis_chain = synthesis_prompt | self.llm
            synthesis_response = await synthesis_chain.ainvoke({
                "title": state["paper_metadata"].get("title", ""),
                "serious_summary": state["serious_summary"],
                "contextual_analysis": state["contextual_analysis"],
                "novelty_analysis": state["novelty_analysis"],
                "human_fun_summary": state["human_fun_summary"]
            })
            
            content = synthesis_response.content
            
            # Parse the response to extract different formats
            # Extract Friend's Take conversation (everything before Twitter thread)
            friend_conversation = ""
            if "1/🧵" in content:
                # Extract everything before the first Twitter thread
                twitter_start = content.find("1/🧵")
                friend_conversation = content[:twitter_start].strip()
            elif "2. TWITTER THREAD" in content:
                # Alternative pattern
                twitter_start = content.find("2. TWITTER THREAD")
                friend_conversation = content[:twitter_start].strip()
            else:
                # Fallback: try to extract conversation by looking for Professor/Friend pattern
                lines = content.split('\n')
                conversation_lines = []
                for line in lines:
                    if ('**Professor:**' in line or '**Friend:**' in line or 
                        line.strip().startswith('"') or 
                        (conversation_lines and not line.strip().startswith(('1/', '2/', '3/', '#', '##')))):
                        conversation_lines.append(line)
                    elif conversation_lines and (line.strip().startswith(('1/', '2/', '3/')) or 
                                               'TWITTER THREAD' in line or 'BLOG POST' in line):
                        break
                friend_conversation = '\n'.join(conversation_lines).strip()
            
            # Clean up the conversation - remove section headers
            friend_conversation = friend_conversation.replace("1. FRIEND'S TAKE - COFFEE CHAT CONVERSATION", "")
            friend_conversation = friend_conversation.replace("FRIEND'S TAKE - COFFEE CHAT CONVERSATION", "")
            friend_conversation = friend_conversation.strip()
            
            state["final_digest"] = friend_conversation if friend_conversation else content
            
            # Extract tweet thread (look for numbered tweets)
            tweets = []
            lines = content.split('\n')
            for line in lines:
                if line.strip() and any(line.strip().startswith(f'{i}/🧵') for i in range(1, 10)):
                    tweets.append(line.strip())
            state["tweet_thread"] = tweets
            
            # Extract blog post (everything after "BLOG POST STRUCTURE" or "3. BLOG POST")
            blog_content = ""
            if "3. BLOG POST STRUCTURE" in content:
                blog_start = content.find("3. BLOG POST STRUCTURE")
                blog_content = content[blog_start:].replace("3. BLOG POST STRUCTURE:", "").strip()
            elif "BLOG POST STRUCTURE" in content:
                blog_start = content.find("BLOG POST STRUCTURE")
                blog_content = content[blog_start:].replace("BLOG POST STRUCTURE:", "").strip()
            
            state["blog_post"] = blog_content if blog_content else ""
            
            state["status"] = ProcessingStatus.COMPLETED
            await self._log_step_complete(state, step_name)
            
        except Exception as e:
            error_msg = f"Output generation failed: {str(e)}"
            state["error_message"] = error_msg
            state["status"] = ProcessingStatus.FAILED
            await self._log_step_error(state, step_name, error_msg)
            
        return state


def create_production_pipeline() -> StateGraph:
    """Create the production LangGraph pipeline"""
    
    nodes = ProductionPipelineNodes()
    workflow = StateGraph(PipelineState)
    
    # Add nodes in the new flow: Ingestion → Parsing → RAG → Summarizer+Context → Novelty → Fun → Output
    workflow.add_node("ingestion", nodes.node_1_ingestion)
    workflow.add_node("parsing", nodes.node_2_parsing)
    workflow.add_node("rag", nodes.node_3_rag)
    workflow.add_node("summarizer_context", nodes.node_4_summarizer_context)
    workflow.add_node("novelty", nodes.node_5_novelty)
    workflow.add_node("fun", nodes.node_6_fun)
    workflow.add_node("output", nodes.node_7_output)
    
    # Define the flow
    workflow.add_edge(START, "ingestion")
    workflow.add_edge("ingestion", "parsing")
    workflow.add_edge("parsing", "rag")
    workflow.add_edge("rag", "summarizer_context")
    workflow.add_edge("summarizer_context", "novelty")
    workflow.add_edge("novelty", "fun")
    workflow.add_edge("fun", "output")
    workflow.add_edge("output", END)
    
    return workflow.compile()
