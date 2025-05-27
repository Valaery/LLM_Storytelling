"""Story browser module for the LLM Story Generator.

This module provides functionality for browsing, searching, and exporting stories
through a Streamlit interface.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import json
from typing import Dict, Any, List, Tuple, Optional

from .db_manager import DatabaseManager

def format_story(story: Tuple) -> Dict[str, Any]:
    """Format a story record for display.
    
    This function converts a raw story tuple from the database into a
    human-readable dictionary with formatted values.
    
    Args:
        story: Story record tuple from the database containing:
            - id: Story ID
            - prompt: User's input prompt
            - response: Generated story text
            - system_prompt: System prompt used
            - style: Story style used
            - created_at: Creation timestamp
            - mode: Generation mode
            - memory_added: Whether story was added to memory
    
    Returns:
        Dict[str, Any]: Formatted story data with human-readable keys and values,
        including formatted timestamps and boolean indicators.
    """
    return {
        "ID": story[0],
        "Prompt": story[1],
        "Response": story[2],
        "System Prompt": story[3],
        "Style": story[4],
        "Created At": datetime.fromisoformat(story[5]).strftime("%Y-%m-%d %H:%M:%S"),
        "Mode": story[6],
        "Memory Added": "Yes" if story[7] else "No"
    }

def story_browser(db_manager: DatabaseManager) -> None:
    """Display the story browser interface.
    
    This function creates a Streamlit interface for browsing, searching, and
    exporting stories. It includes features for:
    - Searching stories by content
    - Filtering stories by style
    - Pagination
    - Story export in various formats
    
    Args:
        db_manager: Database manager instance for story operations.
    """
    st.title("📚 Story Browser")
    
    # Search and filter options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search stories", "")
    
    with col2:
        style_filter = st.selectbox(
            "Filter by style",
            ["All"] + list(db_manager.get_statistics()['stories_by_style'].keys())
        )
    
    # Pagination
    page_size = st.sidebar.slider("Stories per page", 5, 50, 10)
    page = st.sidebar.number_input("Page", 1, 1, 1)
    offset = (page - 1) * page_size
    
    # Get stories based on filters
    if search_query:
        stories = db_manager.search_stories(search_query, limit=page_size, offset=offset)
    elif style_filter != "All":
        stories = db_manager.get_stories_by_style(style_filter, limit=page_size, offset=offset)
    else:
        stories = db_manager.get_all_stories(limit=page_size, offset=offset)
    
    if not stories:
        st.info("No stories found matching your criteria.")
        return
    
    # Display stories
    for story in stories:
        formatted_story = format_story(story)
        
        with st.expander(f"Story #{formatted_story['ID']} - {formatted_story['Created At']}"):
            st.markdown("**Prompt:**")
            st.write(formatted_story['Prompt'])
            
            st.markdown("**Response:**")
            st.write(formatted_story['Response'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Style:** {formatted_story['Style']}")
            with col2:
                st.write(f"**Mode:** {formatted_story['Mode']}")
            with col3:
                st.write(f"**Memory:** {formatted_story['Memory Added']}")
            
            # Show linked documents if any
            docs = db_manager.get_story_documents(formatted_story['ID'])
            if docs:
                st.markdown("**Source Documents:**")
                for doc in docs:
                    st.write(f"- {doc[1]}")
            
            # Export options
            if st.button(f"Export Story #{formatted_story['ID']}", key=f"export_{formatted_story['ID']}"):
                export_story(formatted_story)

def export_story(story: Dict[str, Any]) -> None:
    """Export a story to various formats.
    
    This function provides options to export a story in different formats:
    - JSON: Full story data in JSON format
    - TXT: Formatted text with story details
    - CSV: Story data in CSV format
    
    Args:
        story: Dictionary containing the story data to export.
    """
    export_format = st.selectbox(
        "Select export format",
        ["JSON", "TXT", "CSV"],
        key=f"export_format_{story['ID']}"
    )
    
    if export_format == "JSON":
        st.download_button(
            "Download JSON",
            data=json.dumps(story, indent=2),
            file_name=f"story_{story['ID']}.json",
            mime="application/json"
        )
    elif export_format == "TXT":
        text = f"""Story #{story['ID']}
Created: {story['Created At']}
Style: {story['Style']}
Mode: {story['Mode']}
Memory Added: {story['Memory Added']}

PROMPT:
{story['Prompt']}

RESPONSE:
{story['Response']}
"""
        st.download_button(
            "Download TXT",
            data=text,
            file_name=f"story_{story['ID']}.txt",
            mime="text/plain"
        )
    elif export_format == "CSV":
        df = pd.DataFrame([story])
        st.download_button(
            "Download CSV",
            data=df.to_csv(index=False),
            file_name=f"story_{story['ID']}.csv",
            mime="text/csv"
        ) 