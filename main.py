from arxiv_docs.arxiv_api import *
from arxiv_docs.clean_pdfs import *
from dotenv import load_dotenv


load_dotenv()


if __name__ == "__main__":
    print("Calling the function")
    # search_and_download_arxiv_papers()
    # process_text_files()
    save_chunks_todb()
    print("End...")
    