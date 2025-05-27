"""Test module for the story generator functionality.

This module contains tests for the story generation features, including document
loading, vector store operations, and story generation with and without RAG.
"""
import pytest
import os
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

from llm_story_generator.story_generator import (
    load_documents, append_to_index, load_vectordb,
    store_story_to_memory, generate_story, STORY_STYLES
)

def test_load_documents(test_dirs: Dict[str, str], sample_document: str) -> None:
    """Test loading documents from a directory.
    
    Args:
        test_dirs: Dictionary of test directory paths.
        sample_document: Path to a sample document for testing.
    """
    docs = load_documents(os.path.dirname(sample_document))
    assert len(docs) > 0
    assert any(doc.page_content == "This is a test story document." for doc in docs)

def test_append_to_index(test_dirs: Dict[str, str], sample_document: str) -> None:
    """Test appending documents to the vector index.
    
    Args:
        test_dirs: Dictionary of test directory paths.
        sample_document: Path to a sample document for testing.
    """
    docs = load_documents(os.path.dirname(sample_document))
    vectordb = append_to_index(docs)
    assert vectordb is not None

def test_load_vectordb(test_dirs: Dict[str, str], sample_document: str) -> None:
    """Test loading the vector database.
    
    Args:
        test_dirs: Dictionary of test directory paths.
        sample_document: Path to a sample document for testing.
    """
    # First create the index
    docs = load_documents(os.path.dirname(sample_document))
    append_to_index(docs)
    
    # Then try to load it
    vectordb = load_vectordb()
    assert vectordb is not None

def test_store_story_to_memory(test_dirs: Dict[str, str]) -> None:
    """Test storing a story to memory.
    
    Args:
        test_dirs: Dictionary of test directory paths.
    """
    story_text = "This is a test story"
    timestamp = "2024-01-01T12:00:00"
    
    path = store_story_to_memory(story_text, timestamp)
    assert os.path.exists(path)
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        assert story_text in content
        assert timestamp in content

@patch('llm_story_generator.story_generator.load_llm')
def test_generate_story_direct(mock_load_llm: MagicMock, db_manager: Any) -> None:
    """Test direct story generation without RAG.
    
    Args:
        mock_load_llm: Mocked LLM loader.
        db_manager: Database manager instance.
    """
    # Mock the LLM response
    mock_llm = MagicMock()
    mock_llm.return_value = "Generated story content"
    mock_load_llm.return_value = mock_llm
    
    answer, source_docs, now = generate_story(
        user_input="Write a story",
        selected_style="Creative Storyteller",
        custom_prompt=STORY_STYLES["Creative Storyteller"],
        mode="Direct Generation",
        selected=[],
        db_manager=db_manager
    )
    
    assert answer == "Generated story content"
    assert len(source_docs) == 0
    assert now is not None

@patch('llm_story_generator.story_generator.load_llm')
@patch('llm_story_generator.story_generator.append_to_index')
def test_generate_story_rag(
    mock_append_to_index: MagicMock,
    mock_load_llm: MagicMock,
    db_manager: Any,
    sample_document: str
) -> None:
    """Test story generation with RAG.
    
    Args:
        mock_append_to_index: Mocked index appender.
        mock_load_llm: Mocked LLM loader.
        db_manager: Database manager instance.
        sample_document: Path to a sample document for testing.
    """
    # Mock the vector database and LLM
    mock_vectordb = MagicMock()
    mock_vectordb.as_retriever.return_value = MagicMock()
    mock_append_to_index.return_value = mock_vectordb
    
    mock_llm = MagicMock()
    mock_llm.return_value = "Generated story content"
    mock_load_llm.return_value = mock_llm
    
    answer, source_docs, now = generate_story(
        user_input="Write a story",
        selected_style="Creative Storyteller",
        custom_prompt=STORY_STYLES["Creative Storyteller"],
        mode="RAG with Documents",
        selected=[os.path.basename(sample_document)],
        db_manager=db_manager
    )
    
    assert answer == "Generated story content"
    assert now is not None

def test_story_styles() -> None:
    """Test that story styles are properly defined."""
    assert "Creative Storyteller" in STORY_STYLES
    assert "One Piece Writer" in STORY_STYLES
    
    for style, prompt in STORY_STYLES.items():
        assert isinstance(prompt, str)
        assert len(prompt) > 0 