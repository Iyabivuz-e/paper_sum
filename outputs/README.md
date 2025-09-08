# Outputs Directory

This directory contains the results from processing research papers through the LaughGraph pipeline.

## File Structure

- `{arxiv_id}_result.json` - Complete pipeline output in JSON format
- `{arxiv_id}_digest.md` - Final digest in Markdown format  
- `{arxiv_id}_tweets.txt` - Twitter thread ready for posting
- `{arxiv_id}_blog.md` - Blog post format

## JSON Output Structure

```json
{
  "paper_title": "Paper Title",
  "paper_abstract": "Original abstract",
  "serious_summary": "Technical analysis",
  "human_fun_summary": "Fun translation with humor",
  "contextual_analysis": "How it fits in the field", 
  "novelty_score": 0.7,
  "final_digest": "Blended serious + fun content",
  "tweet_thread": ["1/ Thread starter...", "2/ Main point..."],
  "blog_post": "Structured blog format",
  "processing_status": "completed",
  "paper_metadata": {...}
}
```

This directory is automatically created when you run the pipeline.
