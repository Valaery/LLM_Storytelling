"""Database management module for the LLM Story Generator.

This module provides functionality for managing the SQLite database that stores
stories, documents, and their relationships.
"""
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple

class DatabaseManager:
    """Manages the SQLite database for story and document storage.
    
    This class handles all database operations including story and document storage,
    retrieval, and analytics.
    
    Attributes:
        db_path (str): Path to the SQLite database file.
    """
    
    def __init__(self, db_path: str = "stories.db") -> None:
        """Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file. Defaults to "stories.db".
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database with the schema.
        
        Reads and executes the SQL schema from schema.sql to create the necessary
        tables if they don't exist.
        
        Raises:
            FileNotFoundError: If schema.sql is not found.
            sqlite3.Error: If there's an error executing the schema.
        """
        with open('schema.sql', 'r') as f:
            schema = f.read()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)

    def add_story(
        self,
        prompt: str,
        response: str,
        system_prompt: Optional[str] = None,
        style: Optional[str] = None,
        mode: Optional[str] = None,
        memory_added: bool = False
    ) -> int:
        """Add a new story to the database.
        
        Args:
            prompt: The user's input prompt.
            response: The generated story response.
            system_prompt: Optional system prompt used for generation.
            style: Optional story style used.
            mode: Optional generation mode used.
            memory_added: Whether the story was added to memory.
        
        Returns:
            int: The ID of the newly inserted story.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO stories (prompt, response, system_prompt, style, mode, memory_added)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (prompt, response, system_prompt, style, mode, memory_added))
            return cursor.lastrowid

    def add_document(self, filename: str, file_hash: str) -> int:
        """Add a new document to the database.
        
        Args:
            filename: Name of the document file.
            file_hash: MD5 hash of the document content.
        
        Returns:
            int: The ID of the newly inserted document.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO documents (filename, file_hash)
                VALUES (?, ?)
            """, (filename, file_hash))
            return cursor.lastrowid

    def link_story_to_document(self, story_id: int, document_id: int) -> None:
        """Link a story to a document.
        
        Args:
            story_id: ID of the story to link.
            document_id: ID of the document to link.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO story_documents (story_id, document_id)
                VALUES (?, ?)
            """, (story_id, document_id))

    def get_story(self, story_id: int) -> Optional[Tuple]:
        """Get a story by ID.
        
        Args:
            story_id: ID of the story to retrieve.
        
        Returns:
            Optional[Tuple]: Story data as a tuple, or None if not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stories WHERE id = ?", (story_id,))
            return cursor.fetchone()

    def get_all_stories(self, limit: int = 100, offset: int = 0) -> List[Tuple]:
        """Get all stories with pagination.
        
        Args:
            limit: Maximum number of stories to return.
            offset: Number of stories to skip.
        
        Returns:
            List[Tuple]: List of story data tuples.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM stories 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
            return cursor.fetchall()

    def get_stories_by_style(self, style: str, limit: int = 100, offset: int = 0) -> List[Tuple]:
        """Get stories by style.
        
        Args:
            style: Style to filter stories by.
            limit: Maximum number of stories to return.
            offset: Number of stories to skip.
        
        Returns:
            List[Tuple]: List of story data tuples.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM stories 
                WHERE style = ? 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (style, limit, offset))
            return cursor.fetchall()

    def get_story_documents(self, story_id: int) -> List[Tuple]:
        """Get all documents linked to a story.
        
        Args:
            story_id: ID of the story to get documents for.
        
        Returns:
            List[Tuple]: List of document data tuples.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.* FROM documents d
                JOIN story_documents sd ON d.id = sd.document_id
                WHERE sd.story_id = ?
            """, (story_id,))
            return cursor.fetchall()

    def search_stories(self, query: str, limit: int = 100, offset: int = 0) -> List[Tuple]:
        """Search stories by prompt or response content.
        
        Args:
            query: Search query string.
            limit: Maximum number of stories to return.
            offset: Number of stories to skip.
        
        Returns:
            List[Tuple]: List of matching story data tuples.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM stories 
                WHERE prompt LIKE ? OR response LIKE ?
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (f'%{query}%', f'%{query}%', limit, offset))
            return cursor.fetchall()

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dict[str, Any]: Dictionary containing basic database statistics.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            stats = {}
            
            # Total stories
            cursor.execute("SELECT COUNT(*) FROM stories")
            stats['total_stories'] = cursor.fetchone()[0]
            
            # Stories by style
            cursor.execute("SELECT style, COUNT(*) FROM stories GROUP BY style")
            stats['stories_by_style'] = dict(cursor.fetchall())
            
            # Total documents
            cursor.execute("SELECT COUNT(*) FROM documents")
            stats['total_documents'] = cursor.fetchone()[0]
            
            return stats

    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Get enhanced database statistics.
        
        Returns:
            Dict[str, Any]: Dictionary containing detailed database statistics including:
                - Basic counts (total stories, documents)
                - Stories by style and mode
                - Memory usage statistics
                - Time-based statistics
                - Response length statistics
                - Document usage statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            stats = {}
            
            # Basic stats
            cursor.execute("SELECT COUNT(*) FROM stories")
            stats['total_stories'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM documents")
            stats['total_documents'] = cursor.fetchone()[0]
            
            # Stories by style
            cursor.execute("SELECT style, COUNT(*) FROM stories GROUP BY style")
            stats['stories_by_style'] = dict(cursor.fetchall())
            
            # Stories by mode
            cursor.execute("SELECT mode, COUNT(*) FROM stories GROUP BY mode")
            stats['stories_by_mode'] = dict(cursor.fetchall())
            
            # Memory usage
            cursor.execute("SELECT COUNT(*) FROM stories WHERE memory_added = 1")
            stats['stories_in_memory'] = cursor.fetchone()[0]
            
            # Time-based statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    strftime('%Y-%m-%d', created_at) as date
                FROM stories 
                GROUP BY date 
                ORDER BY date DESC 
                LIMIT 7
            """)
            stats['stories_last_7_days'] = dict(cursor.fetchall())
            
            # Average response length
            cursor.execute("""
                SELECT AVG(length(response)) 
                FROM stories
            """)
            stats['avg_response_length'] = int(cursor.fetchone()[0] or 0)
            
            # Most used documents
            cursor.execute("""
                SELECT d.filename, COUNT(*) as usage_count
                FROM documents d
                JOIN story_documents sd ON d.id = sd.document_id
                GROUP BY d.id
                ORDER BY usage_count DESC
                LIMIT 5
            """)
            stats['most_used_documents'] = dict(cursor.fetchall())
            
            return stats

    def export_all_stories(self, format: str = "json") -> Union[List[Dict[str, Any]], List[Tuple]]:
        """Export all stories in the specified format.
        
        Args:
            format: Export format, either "json" or "csv".
        
        Returns:
            Union[List[Dict[str, Any]], List[Tuple]]: Exported stories in the specified format.
        
        Raises:
            ValueError: If the format is not supported.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stories ORDER BY created_at DESC")
            stories = cursor.fetchall()
            
            if format == "json":
                return [{
                    "id": story[0],
                    "prompt": story[1],
                    "response": story[2],
                    "system_prompt": story[3],
                    "style": story[4],
                    "created_at": story[5],
                    "mode": story[6],
                    "memory_added": bool(story[7])
                } for story in stories]
            elif format == "csv":
                return stories
            else:
                raise ValueError(f"Unsupported format: {format}")

    def get_story_analytics(self, story_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed analytics for a specific story.
        
        Args:
            story_id: ID of the story to analyze.
        
        Returns:
            Optional[Dict[str, Any]]: Dictionary containing story analytics including:
                - Story details
                - Response statistics (length, word count, paragraph count)
                - Used documents
                None if story not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            analytics = {}
            
            # Get story details
            cursor.execute("SELECT * FROM stories WHERE id = ?", (story_id,))
            story = cursor.fetchone()
            if not story:
                return None
                
            analytics['story'] = {
                "id": story[0],
                "prompt": story[1],
                "response": story[2],
                "system_prompt": story[3],
                "style": story[4],
                "created_at": story[5],
                "mode": story[6],
                "memory_added": bool(story[7])
            }
            
            # Get response statistics
            analytics['response_stats'] = {
                "length": len(story[2]),
                "word_count": len(story[2].split()),
                "paragraph_count": len(story[2].split('\n\n'))
            }
            
            # Get document usage
            cursor.execute("""
                SELECT d.filename, d.created_at
                FROM documents d
                JOIN story_documents sd ON d.id = sd.document_id
                WHERE sd.story_id = ?
            """, (story_id,))
            analytics['used_documents'] = [
                {"filename": doc[0], "created_at": doc[1]}
                for doc in cursor.fetchall()
            ]
            
            return analytics 