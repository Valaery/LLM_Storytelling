"""Configuration settings for the LLM Story Generator.

This module contains all configuration settings including paths, model parameters,
vector store settings, and logging configuration.
"""
import os
import logging
from typing import Dict, Any, Final, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger: Final[logging.Logger] = logging.getLogger(__name__)

# Paths
DOCS_PATH: Final[str] = "./docs"
INDEX_PATH: Final[str] = "./faiss_index"
LOG_PATH: Final[str] = "./history.log"
HASH_DB_PATH: Final[str] = "./hash_index.json"
EXPORT_JSON: Final[str] = "./exported_qa.json"
MEMORY_STORIES_PATH: Final[str] = os.path.join(DOCS_PATH, "memory_stories")
DB_PATH: Final[str] = "./story_generator.db"  # SQLite database path

# Server
LLAMA_SERVER_URL: Final[str] = "http://localhost:8000"

# Model settings
MODEL_SETTINGS: Final[Dict[str, Any]] = {
    "model_name": "local-llama",  # Name for the local model
    "temperature": 0.9,
    "max_tokens": 1500,
    "top_p": 0.95,
    "max_input_length": 4096,
    "max_total_tokens": 4096
}

# Local LLM settings
LOCAL_LLM_SETTINGS: Final[Dict[str, Any]] = {
    "base_url": os.getenv("LLAMA_SERVER_URL", "http://localhost:8000/v1"),
    "api_key": "not-needed",  # Required by LangChain but not used for local server
    "model": os.getenv("LLAMA_MODEL", "Qwen3-30B")
}

# Vector store settings
VECTOR_STORE_SETTINGS: Final[Dict[str, Any]] = {
    "chunk_size": 500,
    "chunk_overlap": 50,
    "embedding_model": "all-MiniLM-L6-v2",
    "k": 3  # Number of documents to retrieve for RAG
}

def ensure_directories() -> None:
    """Create necessary directories if they don't exist.
    
    Creates the following directories if they don't exist:
    - DOCS_PATH: Directory for storing documents
    - MEMORY_STORIES_PATH: Directory for storing story memory
    - Directory containing INDEX_PATH: Directory for storing vector indices
    
    Raises:
        Exception: If directory creation fails.
    """
    directories: List[str] = [DOCS_PATH, MEMORY_STORIES_PATH, os.path.dirname(INDEX_PATH)]
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {str(e)}")
            raise

# Create necessary directories
ensure_directories() 