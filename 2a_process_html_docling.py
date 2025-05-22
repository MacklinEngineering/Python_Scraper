import os, sys
import shutil
from pathlib import Path
from docling.document_converter import DocumentConverter
from my_config import MY_CONFIG

shutil.rmtree(MY_CONFIG.PROCESSED_DATA_DIR, ignore_errors=True)
shutil.os.makedirs(MY_CONFIG.PROCESSED_DATA_DIR, exist_ok=True)
print (f"✅ Cleared  processed data directory :  {MY_CONFIG.PROCESSED_DATA_DIR}")

converter = DocumentConverter(format_options={"preserve_links": True})

input_path = Path(MY_CONFIG.CRAWL_DIR)
html_files = list(input_path.glob('*.html')) + list(input_path.glob('*.htm'))
print(f"Found {len(html_files)} HTML files to convert")

for html_file in html_files:
    result = converter.convert(html_file)
    markdown_content = result.document.export_to_markdown()
    
    md_file_name = os.path.join(MY_CONFIG.PROCESSED_DATA_DIR, f"{html_file.stem}.md")
    with open(md_file_name, "w", encoding="utf-8") as md_file:
        md_file.write(markdown_content)
        
    print(f"Converted HTML '{html_file}' to Markdown '{md_file_name}'")
    
print (f"✅ {len(html_files)} HTML files converted to Markdown")