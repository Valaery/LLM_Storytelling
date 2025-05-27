"""Pytest configuration and fixtures for the LLM Story Generator tests.

This module provides test fixtures and configuration for the test suite,
including temporary directory management and database setup.
"""
import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Generator, Any

from llm_story_generator.db_manager import DatabaseManager

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

@pytest.fixture
def test_dirs() -> Generator[Dict[str, str], None, None]:
    """Create temporary directories for testing.
    
    Creates a temporary directory structure with subdirectories for docs,
    memory, and index. Also creates a sample test document.
    
    Yields:
        Dict[str, str]: Dictionary containing paths to test directories and files.
            Keys:
                - temp_dir: Root temporary directory
                - docs_dir: Directory for test documents
                - memory_dir: Directory for memory storage
                - index_dir: Directory for index storage
                - test_doc: Path to sample test document
    
    Note:
        The temporary directory and its contents are automatically cleaned up
        after the test completes.
    """
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Create subdirectories
    docs_dir = os.path.join(temp_dir, "docs")
    memory_dir = os.path.join(temp_dir, "memory")
    index_dir = os.path.join(temp_dir, "index")
    
    os.makedirs(docs_dir)
    os.makedirs(memory_dir)
    os.makedirs(index_dir)
    
    # Create a test document
    test_doc = os.path.join(docs_dir, "test.txt")
    with open(test_doc, "w", encoding="utf-8") as f:
        f.write("This is a test story document.")
    
    yield {
        "temp_dir": temp_dir,
        "docs_dir": docs_dir,
        "memory_dir": memory_dir,
        "index_dir": index_dir,
        "test_doc": test_doc
    }
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_document(test_dirs: Dict[str, str]) -> str:
    """Return the path to a sample document.
    
    Args:
        test_dirs: Dictionary containing test directory paths.
    
    Returns:
        str: Path to the sample test document.
    """
    return test_dirs["test_doc"]

@pytest.fixture
def db_manager(test_dirs: Dict[str, str]) -> DatabaseManager:
    """Create a database manager instance for testing.
    
    Args:
        test_dirs: Dictionary containing test directory paths.
    
    Returns:
        DatabaseManager: A configured database manager instance for testing.
    """
    return DatabaseManager() 