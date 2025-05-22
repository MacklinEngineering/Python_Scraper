"""
May 21, 2025
Nyah Macklin

This crawler is used created to replace the original dpk_web2parquet crawler due to found HTML formatting issues.
Key differences:
1. Uses BeautifulSoup4 for HTML parsing
2. Maintains proper HTML formatting throughout the document (does not break formatting)
3. Added MIME type detection to properly handle different file types (e.g., PDFs vs HTML)
   - This addition was made after discovering that PDF files were being incorrectly processed as HTML
   - The docling processor was failing when trying to parse these misidentified files
4. Improved URL cleaning and validation
"""

import os
import sys
import shutil
import argparse
import requests
import mimetypes
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
from my_config import MY_CONFIG
import logging

# Configure logging to the WARN level
logging.basicConfig(level=logging.WARN)

class WebsiteCrawler:
    def __init__(self, start_url, max_depth, max_downloads, output_folder):
        self.start_url = start_url
        self.max_depth = max_depth
        self.max_downloads = max_downloads
        self.output_folder = output_folder
        self.visited_urls = set()
        self.download_count = 0
        self.domain = urlparse(start_url).netloc

    def clean_url(self, url):
        """Clean and validate the URL."""
        # Remove any whitespace and non-breaking spaces
        url = url.strip().replace('\xa0', '')
        
        # Basic URL validation - must start with http:// or https://
        if not url.startswith(('http://', 'https://')):
            return None
            
        # Parse the URL
        parsed = urlparse(url)
        
        # Check if it's a valid URL (not a text snippet)
        if len(parsed.path) > 500 or ' ' in parsed.path:
            return None
            
        # Remove duplicate domains in path
        path_parts = parsed.path.split('/')
        clean_parts = []
        for part in path_parts:
            if self.domain not in part:
                clean_parts.append(part)
        clean_path = '/'.join(clean_parts)
        
        # Reconstruct the URL
        clean_url = f"{parsed.scheme}://{parsed.netloc}{clean_path}"
        if parsed.query:
            clean_url += f"?{parsed.query}"
            
        return clean_url

    def is_valid_url(self, url):
        """Check if URL is valid and belongs to the same domain."""
        try:
            parsed = urlparse(url)
            return parsed.netloc == self.domain
        except:
            return False

    def get_mime_type(self, response):
        """
        Determine the MIME type of the response content.
        Added to properly handle different file types (HTML, PDF, etc.)
        """
        # First check the Content-Type header
        content_type = response.headers.get('Content-Type', '').split(';')[0].lower()
        if content_type:
            return content_type

        # If no Content-Type header, try to guess from the URL
        url_path = urlparse(response.url).path
        mime_type, _ = mimetypes.guess_type(url_path)
        return mime_type or 'application/octet-stream'

    def save_content(self, url, response, mime_type):
        """
        Save the content based on its MIME type.
        This method handles different file types appropriately.
        """
        # Create filename from URL
        filename = url.replace(self.start_url, '').strip('/')
        if not filename:
            filename = 'index'
        filename = filename.replace('/', '_')

        # Handle different MIME types
        if mime_type == 'text/html':
            # For HTML, use BeautifulSoup to prettify and save as HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            filename = filename + '_text.html'
            content = soup.prettify()
            mode = 'w'
            encoding = 'utf-8'
        else:
            # For non-HTML files (PDFs, images, etc.), save as binary
            ext = mimetypes.guess_extension(mime_type) or '.bin'
            filename = filename + ext
            content = response.content
            mode = 'wb'
            encoding = None

        # Save the file
        filepath = os.path.join(self.output_folder, filename)
        with open(filepath, mode, encoding=encoding) as f:
            f.write(content)

        self.download_count += 1
        return True

    def crawl(self, url, depth=0):
        """Crawl the website starting from the given URL."""
        if depth > self.max_depth or self.download_count >= self.max_downloads:
            return

        # Clean and validate the URL
        url = self.clean_url(url)
        if not url or not self.is_valid_url(url):
            return

        if url in self.visited_urls:
            return

        self.visited_urls.add(url)

        try:
            response = requests.get(url)
            response.raise_for_status()

            # Get MIME type and save content accordingly
            mime_type = self.get_mime_type(response)
            self.save_content(url, response, mime_type)

            # Only look for links in HTML content
            if mime_type == 'text/html':
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href:
                        absolute_url = urljoin(url, href)
                        self.crawl(absolute_url, depth + 1)

        except requests.exceptions.RequestException as e:
            logging.warning(f"Error crawling {url}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Crawl a website and save HTML content')
    parser.add_argument('--url', required=True, help='Starting URL to crawl')
    parser.add_argument('--max-depth', type=int, default=MY_CONFIG.CRAWL_MAX_DEPTH, help='Maximum crawl depth')
    parser.add_argument('--max-downloads', type=int, default=MY_CONFIG.CRAWL_MAX_DOWNLOADS, help='Maximum number of pages to download')
    args = parser.parse_args()

    # Create output directory
    output_dir = os.path.join('workspace', 'crawled')
    os.makedirs(output_dir, exist_ok=True)

    # Initialize and run crawler
    crawler = WebsiteCrawler(args.url, args.max_depth, args.max_downloads, output_dir)
    crawler.crawl(args.url)

if __name__ == '__main__':
    main() 
