"""Test module for the database manager functionality.

This module contains tests for the DatabaseManager class, covering story and document
management, linking, and statistics retrieval.
"""
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

def test_add_story(db_manager: Any, sample_story: Dict[str, Any]) -> None:
    """Test adding a story to the database.
    
    Args:
        db_manager: Database manager instance.
        sample_story: Sample story data for testing.
    """
    story_id = db_manager.add_story(**sample_story)
    assert story_id is not None
    
    # Verify story was added
    story = db_manager.get_story(story_id)
    assert story is not None
    assert story["prompt"] == sample_story["prompt"]
    assert story["response"] == sample_story["response"]
    assert story["style"] == sample_story["style"]
    assert story["mode"] == sample_story["mode"]

def test_add_document(db_manager: Any, sample_document: str) -> None:
    """Test adding a document to the database.
    
    Args:
        db_manager: Database manager instance.
        sample_document: Sample document path for testing.
    """
    doc_id = db_manager.add_document(sample_document, "test_hash")
    assert doc_id is not None
    
    # Verify document was added
    doc = db_manager.get_document(doc_id)
    assert doc is not None
    assert doc["path"] == sample_document
    assert doc["hash"] == "test_hash"

def test_link_story_to_document(
    db_manager: Any,
    sample_story: Dict[str, Any],
    sample_document: str
) -> None:
    """Test linking a story to a document.
    
    Args:
        db_manager: Database manager instance.
        sample_story: Sample story data for testing.
        sample_document: Sample document path for testing.
    """
    story_id = db_manager.add_story(**sample_story)
    doc_id = db_manager.add_document(sample_document, "test_hash")
    
    db_manager.link_story_to_document(story_id, doc_id)
    
    # Verify link was created
    links = db_manager.get_story_documents(story_id)
    assert len(links) == 1
    assert links[0]["document_id"] == doc_id

def test_get_enhanced_statistics(db_manager: Any, sample_story: Dict[str, Any]) -> None:
    """Test getting enhanced statistics.
    
    Args:
        db_manager: Database manager instance.
        sample_story: Sample story data for testing.
    """
    # Add multiple stories with different styles and modes
    db_manager.add_story(**sample_story)
    db_manager.add_story(**{**sample_story, "style": "One Piece Writer"})
    db_manager.add_story(**{**sample_story, "mode": "RAG with Documents"})
    
    stats = db_manager.get_enhanced_statistics()
    
    assert stats["total_stories"] == 3
    assert "Creative Storyteller" in stats["stories_by_style"]
    assert "One Piece Writer" in stats["stories_by_style"]
    assert "Direct Generation" in stats["stories_by_mode"]
    assert "RAG with Documents" in stats["stories_by_mode"]

def test_get_stories_last_7_days(db_manager: Any, sample_story: Dict[str, Any]) -> None:
    """Test getting stories from the last 7 days.
    
    Args:
        db_manager: Database manager instance.
        sample_story: Sample story data for testing.
    """
    # Add a story
    db_manager.add_story(**sample_story)
    
    # Get stories from last 7 days
    stories = db_manager.get_stories_last_7_days()
    assert len(stories) > 0

def test_get_story_by_id(db_manager: Any, sample_story: Dict[str, Any]) -> None:
    """Test retrieving a story by ID.
    
    Args:
        db_manager: Database manager instance.
        sample_story: Sample story data for testing.
    """
    story_id = db_manager.add_story(**sample_story)
    story = db_manager.get_story(story_id)
    
    assert story is not None
    assert story["id"] == story_id
    assert story["prompt"] == sample_story["prompt"]
    assert story["response"] == sample_story["response"]

def test_get_document_by_id(db_manager: Any, sample_document: str) -> None:
    """Test retrieving a document by ID.
    
    Args:
        db_manager: Database manager instance.
        sample_document: Sample document path for testing.
    """
    doc_id = db_manager.add_document(sample_document, "test_hash")
    doc = db_manager.get_document(doc_id)
    
    assert doc is not None
    assert doc["id"] == doc_id
    assert doc["path"] == sample_document
    assert doc["hash"] == "test_hash"

def test_get_story_documents(
    db_manager: Any,
    sample_story: Dict[str, Any],
    sample_document: str
) -> None:
    """Test retrieving documents linked to a story.
    
    Args:
        db_manager: Database manager instance.
        sample_story: Sample story data for testing.
        sample_document: Sample document path for testing.
    """
    story_id = db_manager.add_story(**sample_story)
    doc_id = db_manager.add_document(sample_document, "test_hash")
    db_manager.link_story_to_document(story_id, doc_id)
    
    docs = db_manager.get_story_documents(story_id)
    assert len(docs) == 1
    assert docs[0]["document_id"] == doc_id 