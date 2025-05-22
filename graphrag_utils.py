from typing import List, Dict, Any
import logging
from neo4j import GraphDatabase
from neo4j_graphrag.generation import GraphRAG, RagTemplate
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.embeddings import SentenceTransformerEmbeddings
from neo4j_graphrag.llm import OllamaLLM
from my_config import MY_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphRAGManager:
    def __init__(self):
        self.uri = MY_CONFIG.NEO4J_URI
        self.user = MY_CONFIG.NEO4J_USER
        self.password = MY_CONFIG.NEO4J_PASSWORD
        self.database = MY_CONFIG.NEO4J_DATABASE
        
        logger.info("Initializing Neo4j driver...")
        # Initialize Neo4j driver
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )
        
        # Create vector index if it doesn't exist
        with self.driver.session(database=self.database) as session:
            logger.info("Creating vector index...")
            # Drop existing index if it exists
            session.run(f'DROP INDEX `{MY_CONFIG.NEO4J_VECTOR_INDEX}` IF EXISTS')
            
            # Create new vector index
            session.run(f"""
            CREATE VECTOR INDEX `{MY_CONFIG.NEO4J_VECTOR_INDEX}`
            FOR (n:Document)
            ON (n.embedding)
            OPTIONS {{indexConfig: {{
                `vector.dimensions`: {MY_CONFIG.EMBEDDING_LENGTH},
                `vector.similarity_function`: 'cosine'
            }}}}
            """)
        
        logger.info("Initializing embeddings...")
        # Initialize embeddings using HuggingFace model via sentence-transformers
        self.embeddings = SentenceTransformerEmbeddings(MY_CONFIG.EMBEDDING_MODEL)
        
        logger.info("Initializing vector retriever...")
        # Initialize vector retriever
        self.retriever = VectorRetriever(
            driver=self.driver,
            index_name=MY_CONFIG.NEO4J_VECTOR_INDEX,
            embedder=self.embeddings
        )
        
        # Initialize LLM based on environment
        logger.info("Initializing LLM...")
        if MY_CONFIG.LLM_RUN_ENV == 'local_ollama':
            self.llm = OllamaLLM(
                model_name=MY_CONFIG.LLM_MODEL
            )
        else:
            raise ValueError(f"Unsupported LLM environment: {MY_CONFIG.LLM_RUN_ENV}")
        
        # Create a custom prompt template using RagTemplate
        prompt_template = RagTemplate(
            template="""You are a helpful AI assistant. Your task is to answer questions using ONLY the information provided in the context below.
DO NOT use any external knowledge or make up information.
If the answer cannot be found in the context, simply state that you cannot answer based on the available information.

When answering questions:
1. Focus on information explicitly stated in the context
2. If multiple pieces of evidence exist, consider all of them
3. If there are contradictions, mention them
4. If the information is unclear or ambiguous, say so

Context:
{context}

Examples:
{examples}

Question:
{query_text}

Answer (using ONLY information from the context above):"""
        )
        
        logger.info("Initializing GraphRAG...")
        # Initialize GraphRAG with custom prompt
        self.graph_rag = GraphRAG(
            retriever=self.retriever,
            llm=self.llm,
            prompt_template=prompt_template
        )
        
        logger.info("Initialization complete!")
    
    def create_knowledge_graph(self, documents: List[Dict[str, Any]]):
        """
        Create a knowledge graph from the processed documents.
        
        Args:
            documents: List of document dictionaries with 'content' and 'metadata'
        """
        logger.info(f"Creating knowledge graph from {len(documents)} documents...")
        for doc in documents:
            content = doc['content']
            metadata = doc.get('metadata', {})
            
            # Create document node with embeddings
            vector = self.embeddings.embed_query(content)
            
            # Create the document node with vector embedding
            with self.driver.session(database=self.database) as session:
                session.run(
                    """
                    CREATE (d:Document {
                        content: $content,
                        source: $source,
                        title: $title,
                        filename: $filename,
                        last_modified: $last_modified,
                        created: $created,
                        embedding: $embedding
                    })
                    """,
                    content=content,
                    source=metadata.get('source', ''),
                    title=metadata.get('title', ''),
                    filename=metadata.get('filename', ''),
                    last_modified=metadata.get('last_modified', ''),
                    created=metadata.get('created', ''),
                    embedding=vector
                )
        logger.info("Knowledge graph creation complete!")
    
    def query(self, query_text: str, top_k: int = 25) -> str:
        """
        Query the knowledge graph using GraphRAG.
        
        Args:
            query_text: The query text
            top_k: Number of results to return. Higher values provide more context but may increase noise.
            
        Returns:
            Answer from the LLM based on retrieved context
        """
        logger.info(f"Processing query: {query_text}")
        try:
            logger.info("Searching knowledge graph...")
            response = self.graph_rag.search(
                query_text=query_text,
                retriever_config={"top_k": top_k}
            )
            logger.info("Search complete, processing response...")
            
            # Handle both string and Message response types
            if hasattr(response, 'content'):
                return response.content
            return str(response)
        except Exception as e:
            logger.error(f"Error during query: {str(e)}")
            return f"Error processing query: {str(e)}"
    
    def close(self):
        """Close the Neo4j driver connection."""
        logger.info("Closing Neo4j driver connection...")
        self.driver.close()
        logger.info("Connection closed.")

class GraphRAGQueryEngineWrapper:
    def __init__(self, top_k=25):
        self.manager = GraphRAGManager()
        self.top_k = top_k
    def as_query_engine(self):
        # Return a callable object for compatibility
        class QueryEngine:
            def __init__(self, manager, top_k):
                self.manager = manager
                self.top_k = top_k
            def query(self, query_text):
                return self.manager.query(query_text, top_k=self.top_k)
        return QueryEngine(self.manager, self.top_k)
    def close(self):
        self.manager.close()

def get_graphrag_index(top_k=25):
    """
    Returns a wrapper compatible with the app's vector_index usage.
    """
    return GraphRAGQueryEngineWrapper(top_k=top_k) 