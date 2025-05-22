"""
Processing HTML Files using BeautifulSoup4 with enhanced text chunking
This script is designed to work with HTML files crawled by the BS4 crawler (1_crawl_site_bs4.py)
"""

import os
import sys
import shutil
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Tuple
from my_config import MY_CONFIG
import json

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        # If this is not the first chunk, include overlap from previous chunk
        if start > 0:
            start = start - overlap
        # If this is not the last chunk, try to break at a sentence boundary
        if end < text_len:
            # Look for sentence boundaries (., !, ?) followed by whitespace
            for i in range(min(end + 100, text_len) - 1, end - 100, -1):
                if i > 0 and text[i] in '.!?' and text[i + 1].isspace():
                    end = i + 1
                    break
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end
    return chunks

def extract_metadata(html_content: str, file_path: str) -> Dict[str, Any]:
    """Extract metadata from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Get title
    title = soup.title.string if soup.title else ''
    
    # Get meta description
    meta_desc = ''
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_tag:
        meta_desc = meta_tag.get('content', '')
    
    # Get main content type based on filename
    content_type = 'unknown'
    filename = os.path.basename(file_path).lower()
    if 'members' in filename:
        content_type = 'member_list'
    elif 'about' in filename:
        content_type = 'about'
    elif 'news' in filename:
        content_type = 'news'
    
    return {
        'title': title,
        'description': meta_desc,
        'content_type': content_type,
        'source_file': file_path
    }

def html_to_markdown(soup: BeautifulSoup) -> str:
    """Convert HTML content to markdown format using BeautifulSoup."""
    # Get the main content
    main_content = soup.find('main')
    if not main_content:
        main_content = soup.body
    
    if not main_content:
        return ""

    # Extract text while preserving important structure
    markdown_lines = []
    
    # Process headings
    for tag in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        level = int(tag.name[1])
        markdown_lines.append('#' * level + ' ' + tag.get_text().strip())
        markdown_lines.append('')
    
    # Process paragraphs and lists
    for tag in main_content.find_all(['p', 'ul', 'ol']):
        if tag.name == 'p':
            text = tag.get_text().strip()
            if text:
                markdown_lines.append(text)
                markdown_lines.append('')
        elif tag.name in ['ul', 'ol']:
            for li in tag.find_all('li'):
                text = li.get_text().strip()
                if text:
                    markdown_lines.append(f"- {text}")
            markdown_lines.append('')
    
    # Process links
    for link in main_content.find_all('a'):
        text = link.get_text().strip()
        href = link.get('href', '')
        if text and href:
            markdown_lines.append(f"[{text}]({href})")
    
    return '\n'.join(markdown_lines)

def process_html_file(html_file: str) -> List[Dict[str, Any]]:
    """Process a single HTML file into chunks with metadata."""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract metadata
    metadata = extract_metadata(html_content, html_file)
    
    # Convert HTML to markdown
    markdown_content = html_to_markdown(soup)
    
    # Split into chunks
    chunks = chunk_text(markdown_content)
    
    # Create documents with chunks and metadata
    documents = []
    for i, chunk in enumerate(chunks):
        doc = {
            'content': chunk,
            'metadata': {
                **metadata,
                'chunk_index': i,
                'total_chunks': len(chunks)
            }
        }
        documents.append(doc)
    
    return documents

def main():
    """Main function to process HTML files with chunking."""
    # Clear directories
    shutil.rmtree(MY_CONFIG.PROCESSED_DATA_DIR, ignore_errors=True)
    os.makedirs(MY_CONFIG.PROCESSED_DATA_DIR, exist_ok=True)
    print(f"✅ Cleared processed data directory: {MY_CONFIG.PROCESSED_DATA_DIR}")
    
    # Process all HTML files from BS4 crawler
    input_path = os.path.join(MY_CONFIG.CRAWL_DIR)
    html_files = [f for f in os.listdir(input_path) 
                 if f.endswith('_text.html')]
    print(f"Found {len(html_files)} HTML files to process")
    
    all_documents = []
    for html_file in html_files:
        file_path = os.path.join(input_path, html_file)
        documents = process_html_file(file_path)
        all_documents.extend(documents)
        
        # Save the first chunk as a markdown file for reference
        if documents:
            md_file_name = os.path.join(
                MY_CONFIG.PROCESSED_DATA_DIR, 
                f"{os.path.splitext(html_file)[0]}.md"
            )
            with open(md_file_name, 'w', encoding='utf-8') as md_file:
                md_file.write(documents[0]['content'])
        
        print(f"Processed HTML '{html_file}' into {len(documents)} chunks")
    
    # Save all documents with metadata for the graph database
    docs_file = os.path.join(MY_CONFIG.PROCESSED_DATA_DIR, 'processed_documents.jsonl')
    with open(docs_file, 'w', encoding='utf-8') as f:
        for doc in all_documents:
            f.write(json.dumps(doc) + '\n')
    
    print(f"✅ Created {len(all_documents)} document chunks from {len(html_files)} HTML files")
    print(f"✅ Saved document chunks to {docs_file}")

if __name__ == "__main__":
    main() 