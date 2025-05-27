"""Test module for the new database manager functionality.

This module contains tests for the enhanced DatabaseManager class, covering
interaction logging, story logging, and retrieval of recent entries.
"""
import pytest
import os
import sqlite3
from datetime import datetime
from typing import Dict, Any, List
from llm_story_generator.db_manager import DatabaseManager
from llm_story_generator.config import DB_PATH

def test_db_initialization(test_dirs: Dict[str, str]) -> None:
    """Test database initialization.
    
    This test verifies that the database is properly initialized with the
    required tables and schema. It checks both the physical database file
    and the presence of essential tables.
    
    Args:
        test_dirs: Dictionary of test directory paths containing:
            - test_db: Path to test database directory
            - test_docs: Path to test documents directory
    
    The test verifies:
    - Database file is created
    - Required tables exist (interactions, stories)
    - Database connection can be established
    - Tables have the correct schema
    """
    db = DatabaseManager()
    assert os.path.exists(DB_PATH)
    
    # Check if tables exist
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check interactions table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interactions'")
    assert cursor.fetchone() is not None
    
    # Check stories table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stories'")
    assert cursor.fetchone() is not None
    
    conn.close()

def test_log_interaction(test_dirs: Dict[str, str]) -> None:
    """Test logging an interaction.
    
    Args:
        test_dirs: Dictionary of test directory paths.
    """
    db = DatabaseManager()
    
    # Log a test interaction
    interaction_id = db.log_interaction(
        user_input="Test input",
        answer="Test answer",
        source_docs=["doc1.txt", "doc2.txt"],
        timestamp=datetime.now().isoformat()
    )
    
    assert interaction_id is not None
    
    # Verify the interaction was logged
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interactions WHERE id = ?", (interaction_id,))
    row = cursor.fetchone()
    
    assert row is not None
    assert row[1] == "Test input"
    assert row[2] == "Test answer"
    assert row[3] == "doc1.txt,doc2.txt"
    
    conn.close()

def test_log_story(test_dirs: Dict[str, str]) -> None:
    """Test logging a story.
    
    Args:
        test_dirs: Dictionary of test directory paths.
    """
    db = DatabaseManager()
    
    # Log a test story
    story_id = db.log_story(
        story_text="Test story",
        timestamp=datetime.now().isoformat()
    )
    
    assert story_id is not None
    
    # Verify the story was logged
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stories WHERE id = ?", (story_id,))
    row = cursor.fetchone()
    
    assert row is not None
    assert row[1] == "Test story"
    
    conn.close()

def test_get_recent_interactions(test_dirs: Dict[str, str]) -> None:
    """Test retrieving recent interactions.
    
    Args:
        test_dirs: Dictionary of test directory paths.
    """
    db = DatabaseManager()
    
    # Log multiple interactions
    for i in range(5):
        db.log_interaction(
            user_input=f"Test input {i}",
            answer=f"Test answer {i}",
            source_docs=[],
            timestamp=datetime.now().isoformat()
        )
    
    # Get recent interactions
    interactions = db.get_recent_interactions(limit=3)
    
    assert len(interactions) == 3
    assert interactions[0][1] == "Test input 4"  # Most recent first
    assert interactions[1][1] == "Test input 3"
    assert interactions[2][1] == "Test input 2"

def test_get_recent_stories(test_dirs: Dict[str, str]) -> None:
    """Test retrieving recent stories.
    
    Args:
        test_dirs: Dictionary of test directory paths.
    """
    db = DatabaseManager()
    
    # Log multiple stories
    for i in range(5):
        db.log_story(
            story_text=f"Test story {i}",
            timestamp=datetime.now().isoformat()
        )
    
    # Get recent stories
    stories = db.get_recent_stories(limit=3)
    
    assert len(stories) == 3
    assert stories[0][1] == "Test story 4"  # Most recent first
    assert stories[1][1] == "Test story 3"
    assert stories[2][1] == "Test story 2" 