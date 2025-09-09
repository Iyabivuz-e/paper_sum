#!/usr/bin/env python3
"""
Quick fix script to convert state.attribute to state["attribute"] in pipeline nodes
"""

import re

# Read the file
with open('/home/dio/Public/learning/paper_sum/app/pipeline/nodes.py', 'r') as f:
    content = f.read()

# Define replacements for common state attributes
replacements = [
    (r'state\.arxiv_id', 'state["arxiv_id"]'),
    (r'state\.pdf_url', 'state["pdf_url"]'),
    (r'state\.user_query', 'state["user_query"]'),
    (r'state\.paper_metadata', 'state["paper_metadata"]'),
    (r'state\.pdf_path', 'state["pdf_path"]'),
    (r'state\.paper_content', 'state["paper_content"]'),
    (r'state\.text_chunks', 'state["text_chunks"]'),
    (r'state\.chunk_ids', 'state["chunk_ids"]'),
    (r'state\.retrieved_context', 'state["retrieved_context"]'),
    (r'state\.serious_summary', 'state["serious_summary"]'),
    (r'state\.contextual_analysis', 'state["contextual_analysis"]'),
    (r'state\.novelty_score', 'state["novelty_score"]'),
    (r'state\.novelty_analysis', 'state["novelty_analysis"]'),
    (r'state\.human_fun_summary', 'state["human_fun_summary"]'),
    (r'state\.final_digest', 'state["final_digest"]'),
    (r'state\.tweet_thread', 'state["tweet_thread"]'),
    (r'state\.blog_post', 'state["blog_post"]'),
    (r'state\.status', 'state["status"]'),
    (r'state\.error_message', 'state["error_message"]'),
    (r'state\.current_step', 'state["current_step"]'),
    (r'state\.processing_steps', 'state["processing_steps"]'),
]

# Apply replacements
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Write back
with open('/home/dio/Public/learning/paper_sum/app/pipeline/nodes.py', 'w') as f:
    f.write(content)

print("✅ Fixed all state attribute accesses in pipeline nodes")
