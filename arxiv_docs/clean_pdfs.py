# ---- This file parses and cleans all the pdfs and chunks them for the RAG  application
import fitz
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# A function to parse pdfs, clean it and save them.
def parse_pdfs():
    folder = Path("./research_papers")
    output = folder/"extraacted_pdfs"
    
    output.mkdir(exist_ok=True)
    
    for pdf_file in folder.glob("*.pdf"):
        raw_pdf = fitz.open(pdf_file)
        
        text_content=""
        for page in raw_pdf:
            blocks = page.get_text("blocks")
            # Sort blocks by vertical position (y0) to preserve reading order
            blocks.sort(key=lambda b: b[1])
            for b in blocks:
                text_content += b[4] + "\n"

        
        #  Create output text file named after the PDF
        output_file = output / f"{pdf_file.stem}.txt"
        with open(output_file, "w", encoding="utf8") as f:
            f.write(text_content)            
            

## A function to split the pdf data into chunks for the RAG system
def process_text_files():
    # Load the files to be chunked
    output = Path("research_papers/extraacted_pdfs")
    
    
    all_chunks_by_file = {}
    
    for file in output.glob("*.txt"):
        loader = TextLoader(file)
        documents = loader.load() ### Document is now loaded
        
        text_spliter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=50
        )
        chunks = text_spliter.split_documents(documents)
        all_chunks_by_file[str(file)] = chunks
        
    return all_chunks_by_file



def save_chunks_todb():
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5"
    )
    vectore_store = Chroma(
        collection_name="arxiv_papers",
        embedding_function=embeddings,
        persist_directory="./db/chroma_store"
    )
    chunks_by_file = process_text_files()
    all_chunks = []
    
    for file_chunks in chunks_by_file.values():
        all_chunks.extend(file_chunks)
        
    vectore_store.add_documents(all_chunks)



