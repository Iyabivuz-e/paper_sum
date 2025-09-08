# """
# LaughGraph: Main CLI and Legacy Compatibility
# Provides both new API functionality and backward compatibility
# """

# import asyncio
# import argparse
# from pathlib import Path
# import json

# # Legacy imports
# from arxiv_docs.arxiv_api import search_and_download_arxiv_papers
# from arxiv_docs.clean_pdfs import parse_pdfs, save_chunks_todb

# # New production imports
# from app.services.pipeline_service import PipelineService
# from app.models.schemas import PaperProcessRequest
# from app.core.config import settings


# async def run_single_paper_pipeline(arxiv_id: str, user_query: str = ""):
#     """Run the complete pipeline for a single paper using new production code"""
#     print(f"🚀 Starting LaughGraph pipeline for arXiv ID: {arxiv_id}")
    
#     try:
#         # Initialize pipeline service
#         service = PipelineService()
        
#         # Create request
#         request = PaperProcessRequest(
#             arxiv_id=arxiv_id,
#             user_query=user_query
#         )
        
#         # Create and process job
#         job_response = await service.create_job(request)
#         print(f"📝 Created job: {job_response.job_id}")
        
#         # Process the paper
#         await service.process_paper_async(job_response.job_id, request)
        
#         # Get results
#         final_result = await service.get_job_status(job_response.job_id)
        
#         if final_result and final_result.analysis_result:
#             print("✅ Pipeline completed successfully!")
            
#             # Print results
#             print("\n" + "="*50)
#             print("📄 PAPER TITLE:")
#             print(final_result.paper_metadata.title if final_result.paper_metadata else "Unknown")
#             print("\n" + "="*50)
#             print("🎯 SERIOUS SUMMARY:")
#             print(final_result.analysis_result.serious_summary)
#             print("\n" + "="*50) 
#             print("😄 FUN SUMMARY:")
#             print(final_result.analysis_result.human_fun_summary)
#             print("\n" + "="*50)
#             print("🔗 FINAL DIGEST:")
#             print(final_result.analysis_result.final_digest)
#             print("\n" + "="*50)
#             print("🐦 TWITTER THREAD:")
#             for i, tweet in enumerate(final_result.analysis_result.tweet_thread, 1):
#                 print(f"{i}. {tweet}")
                
#             return final_result
#         else:
#             print(f"❌ Pipeline failed: {final_result.error_message if final_result else 'Unknown error'}")
#             return None
            
#     except Exception as e:
#         print(f"💥 Error running pipeline: {str(e)}")
#         return None


# def run_batch_processing():
#     """Run the old batch processing workflow (legacy)"""
#     print("🔄 Running legacy batch processing workflow...")
    
#     # Download papers
#     print("📥 Downloading papers from arXiv...")
#     search_and_download_arxiv_papers()
    
#     # Parse PDFs
#     print("📄 Parsing PDFs...")
#     parse_pdfs()
    
#     # Save to vector DB
#     print("💾 Saving chunks to vector database...")
#     save_chunks_todb()
    
#     print("✅ Batch processing completed!")


# def interactive_mode():
#     """Interactive mode for testing individual papers"""
#     print("\n🎭 Welcome to LaughGraph Interactive Mode!")
#     print("Enter arXiv IDs to process papers (e.g., '2310.06825')")
#     print("Type 'batch' for legacy batch processing, 'api' to start API server, 'quit' to exit")
    
#     while True:
#         user_input = input("\n📝 Enter command: ").strip()
        
#         if user_input.lower() == 'quit':
#             print("👋 Goodbye!")
#             break
#         elif user_input.lower() == 'batch':
#             run_batch_processing()
#         elif user_input.lower() == 'api':
#             start_api_server()
#         elif user_input:
#             # Run async function
#             asyncio.run(run_single_paper_pipeline(user_input))
#         else:
#             print("❌ Please enter a valid command")


# def start_api_server():
#     """Start the FastAPI server"""
#     try:
#         import uvicorn
#         from app.main import app
        
#         print("🚀 Starting LaughGraph API Server...")
#         print(f"📍 Server will be available at: http://{settings.host}:{settings.port}")
#         print(f"📚 API docs will be available at: http://{settings.host}:{settings.port}/docs")
        
#         uvicorn.run(
#             "app.main:app",
#             host=settings.host,
#             port=settings.port,
#             reload=settings.debug,
#             workers=1 if settings.debug else settings.workers,
#             log_level=settings.log_level.lower()
#         )
        
#     except ImportError:
#         print("❌ FastAPI dependencies not installed. Please run: uv sync")
#     except Exception as e:
#         print(f"❌ Failed to start API server: {str(e)}")


# def main():
#     """Main CLI entry point"""
#     parser = argparse.ArgumentParser(description="LaughGraph: Serious + Human-Fun AI Research Digest")
    
#     parser.add_argument(
#         'command', 
#         nargs='?', 
#         choices=['api', 'process', 'batch', 'interactive'],
#         default='interactive',
#         help='Command to run'
#     )
    
#     parser.add_argument(
#         '--arxiv-id',
#         type=str,
#         help='ArXiv ID to process (e.g., 2310.06825)'
#     )
    
#     parser.add_argument(
#         '--query',
#         type=str,
#         default='',
#         help='User query or focus area'
#     )
    
#     args = parser.parse_args()
    
#     print("🎭 LaughGraph: Serious + Human-Fun AI Research Digest")
#     print("=" * 60)
    
#     if args.command == 'api':
#         start_api_server()
#     elif args.command == 'process':
#         if not args.arxiv_id:
#             print("❌ --arxiv-id is required for process command")
#             return
#         asyncio.run(run_single_paper_pipeline(args.arxiv_id, args.query))
#     elif args.command == 'batch':
#         run_batch_processing()
#     else:  # interactive
#         interactive_mode()


# if __name__ == "__main__":
#     main()

# from nodes.llm_nodes import process_paper, create_pipeline
# from arxiv_docs.arxiv_api import search_and_download_arxiv_papers
# from arxiv_docs.clean_pdfs import parse_pdfs, save_chunks_todb
# from dotenv import load_dotenv
# import json
# from pathlib import Path

# load_dotenv()


# def run_single_paper_pipeline(arxiv_id: str):
#     """Run the complete pipeline for a single paper"""
#     print(f"🚀 Starting LaughGraph pipeline for arXiv ID: {arxiv_id}")
    
#     try:
#         # Run the LangGraph pipeline
#         result = process_paper(arxiv_id)
        
#         if result["processing_status"] == "completed":
#             print("✅ Pipeline completed successfully!")
            
#             # Save results
#             output_dir = Path("outputs")
#             output_dir.mkdir(exist_ok=True)
            
#             # Save as JSON
#             with open(output_dir / f"{arxiv_id.replace('/', '_')}_result.json", "w") as f:
#                 json.dump(result, f, indent=2, default=str)
            
#             # Print results
#             print("\n" + "="*50)
#             print("📄 PAPER TITLE:")
#             print(result["paper_title"])
#             print("\n" + "="*50)
#             print("🎯 SERIOUS SUMMARY:")
#             print(result["serious_summary"])
#             print("\n" + "="*50) 
#             print("😄 FUN SUMMARY:")
#             print(result["human_fun_summary"])
#             print("\n" + "="*50)
#             print("🔗 FINAL DIGEST:")
#             print(result["final_digest"])
#             print("\n" + "="*50)
#             print("🐦 TWITTER THREAD:")
#             for i, tweet in enumerate(result["tweet_thread"], 1):
#                 print(f"{i}. {tweet}")
            
#         else:
#             print(f"❌ Pipeline failed: {result.get('error_message', 'Unknown error')}")
            
#     except Exception as e:
#         print(f"💥 Error running pipeline: {str(e)}")


# def run_batch_processing():
#     """Run the old batch processing workflow"""
#     print("🔄 Running batch processing workflow...")
    
#     # Download papers
#     print("📥 Downloading papers from arXiv...")
#     search_and_download_arxiv_papers()
    
#     # Parse PDFs
#     print("📄 Parsing PDFs...")
#     parse_pdfs()
    
#     # Save to vector DB
#     print("💾 Saving chunks to vector database...")
#     save_chunks_todb()
    
#     print("✅ Batch processing completed!")


# def interactive_mode():
#     """Interactive mode for testing individual papers"""
#     print("\n🎭 Welcome to LaughGraph Interactive Mode!")
#     print("Enter arXiv IDs to process papers (e.g., '2310.06825')")
#     print("Type 'batch' for batch processing, 'quit' to exit")
    
#     while True:
#         user_input = input("\n📝 Enter arXiv ID (or command): ").strip()
        
#         if user_input.lower() == 'quit':
#             print("👋 Goodbye!")
#             break
#         elif user_input.lower() == 'batch':
#             run_batch_processing()
#         elif user_input:
#             run_single_paper_pipeline(user_input)
#         else:
#             print("❌ Please enter a valid arXiv ID")


# if __name__ == "__main__":
#     print("🎭 LaughGraph: Serious + Human-Fun AI Research Digest")
#     print("=" * 60)
    
#     # Example: Process a specific paper
#     run_single_paper_pipeline("2310.06825")  # Uncomment to test
    
#     # Run interactive mode
#     interactive_mode()
    
#     print("End...")
    