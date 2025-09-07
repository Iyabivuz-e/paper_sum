# --- This is the function that will fetch the research papers and download their respective pdfs
import arxiv # type: ignore

def search_and_download_arxiv_papers():
    client = arxiv.Client()

    search = arxiv.Search(
        query="large language models",
        max_results=10,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    results = client.results(search)
    
    for result in results:
        
        filename = result.title
        if not filename.lower().endswith("pdf"):
            filename += ".pdf"
        result.download_pdf(dirpath="./research_papers", filename=filename)
        # print(f"Title: {result.title}")
        # print(f"Url for pdf: {result.pdf_url}")
        # print(f"Book Id: {result.entry_id}")
        # print(f"Summary: {result.summary}")
        


