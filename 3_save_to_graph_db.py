'''
May 21, 2025
Nyah Macklin
This file saves the text recieved from beautifulsoups' crawler and saves it to the Neo4j graph db.

'''


import os
import json
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm

from my_config import MY_CONFIG
from graphrag_utils import GraphRAGManager

def load_processed_documents() -> List[Dict[str, Any]]:
    """Load processed documents from JSONL file."""
    docs_file = os.path.join(MY_CONFIG.PROCESSED_DATA_DIR, 'processed_documents.jsonl')
    documents = []
    
    with open(docs_file, 'r', encoding='utf-8') as f:
        for line in f:
            doc = json.loads(line)
            documents.append(doc)
    
    return documents

def save_to_graph_db(documents: List[Dict[str, Any]]):
    """Save documents to Neo4j using GraphRAG."""
    graph_manager = GraphRAGManager()
    
    try:
        # Create knowledge graph from documents
        print("Creating knowledge graph from documents...")
        graph_manager.create_knowledge_graph(documents)
        print("Successfully created knowledge graph!")
        
    finally:
        graph_manager.close()

def main():
    """Main function to load processed documents and save them to Neo4j."""
    print("\nLoading processed documents...")
    documents = load_processed_documents()
    print(f"✅ Loaded {len(documents)} document chunks")
    
    print("\nSaving to Neo4j graph database...")
    save_to_graph_db(documents)
    print("Done!")

if __name__ == "__main__":
    main() 
