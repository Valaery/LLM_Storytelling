"""Test configuration and fixtures for the LLM Story Generator tests.

This module provides pytest fixtures for setting up test environments, including
test directories, database instances, and sample data.
"""
import pytest
import os
import shutil
from typing import Dict, Any, Generator
from llm_story_generator.db_manager import DatabaseManager
from llm_story_generator.config import DOCS_PATH, MEMORY_STORIES_PATH, INDEX_PATH, HASH_DB_PATH

@pytest.fixture(scope="session")
def test_dirs() -> Generator[Dict[str, str], None, None]:
    """Create and clean up test directories.
    
    This fixture creates the necessary test directories and cleans them up after
    all tests are complete.
    
    Yields:
        Dict[str, str]: Dictionary containing paths to test directories.
    """
    # Create test directories
    os.makedirs(DOCS_PATH, exist_ok=True)
    os.makedirs(MEMORY_STORIES_PATH, exist_ok=True)
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    
    yield {
        "docs": DOCS_PATH,
        "memory": MEMORY_STORIES_PATH,
        "index": INDEX_PATH
    }
    
    # Cleanup after tests
    if os.path.exists(DOCS_PATH):
        shutil.rmtree(DOCS_PATH)
    if os.path.exists(INDEX_PATH):
        shutil.rmtree(INDEX_PATH)
    if os.path.exists(HASH_DB_PATH):
        os.remove(HASH_DB_PATH)

@pytest.fixture
def db_manager() -> Generator[DatabaseManager, None, None]:
    """Create a test database manager.
    
    This fixture creates a fresh database instance for each test and cleans it up
    afterward.
    
    Yields:
        DatabaseManager: Database manager instance for testing.
    """
    db = DatabaseManager()
    db.create_tables()
    yield db
    # Cleanup after each test
    db.drop_tables()

@pytest.fixture
def sample_story() -> Dict[str, Any]:
    """Return a sample story for testing.
    
    Returns:
        Dict[str, Any]: Sample story data with all required fields.
    """
    return {
        "prompt": "Write a story about a brave knight",
        "response": "Once upon a time, there was a brave knight...",
        "system_prompt": "You are a creative storyteller",
        "style": "Creative Storyteller",
        "mode": "Direct Generation",
        "memory_added": False
    }

@pytest.fixture
def sample_document() -> str:
    """Create a sample document for testing.
    
    Returns:
        str: Path to the created sample document.
    """
    doc_path = os.path.join(DOCS_PATH, "test_story.txt")
    content = "This is a test story document."
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(content)
    return doc_path 