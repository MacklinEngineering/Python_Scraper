"""
May 21, 2025
Nyah Macklin

This file queries the knowledge graph created from the process and then serves it to the LLM as context to answer questions. 
"""

import os
from typing import List, Dict, Any

from my_config import MY_CONFIG
from graphrag_utils import GraphRAGManager

def query_knowledge_graph(query_text: str, top_k: int = 5) -> str:
    """
    Query the knowledge graph using GraphRAG.
    
    Args:
        query_text: The query text
        top_k: Number of results to return
        
    Returns:
        Answer from the LLM based on retrieved context
    """
    graph_manager = GraphRAGManager()
    try:
        return graph_manager.query(query_text, top_k=top_k)
    finally:
        graph_manager.close()

def main():
    """Main function to handle queries."""
    print("AllyCat GraphRAG Query")
    print("Type 'exit' to quit\n")
    
    while True:
        query = input("\nEnter your question: ").strip()
        
        if query.lower() == 'exit':
            break
        
        if not query:
            continue
        
        print("\nSearching knowledge graph and generating answer...")
        answer = query_knowledge_graph(query)
        
        print("\nAnswer:")
        print(answer)
        print("\n" + "-"*50)

if __name__ == "__main__":
    main() 
