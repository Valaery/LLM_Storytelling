"""Main module for the LLM Story Generator application.

This module provides the main Streamlit interface for the LLM Story Generator,
including story generation, browsing, and analytics features.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

from llm_story_generator.db_manager import DatabaseManager
from llm_story_generator.story_browser import story_browser
from llm_story_generator.story_generator import (
    STORY_STYLES,
    generate_story,
    store_story_to_memory,
    append_to_index
)
from llm_story_generator.config import DOCS_PATH, MEMORY_STORIES_PATH
from langchain.docstore.document import Document

# Initialize database
db = DatabaseManager()

def show_analytics() -> None:
    """Display the analytics dashboard.
    
    This function creates a Streamlit interface showing various analytics about
    the generated stories, including:
    - Basic statistics (total stories, memory usage, response lengths)
    - Story distribution by style and mode
    - Activity over time
    - Document usage statistics
    
    The dashboard includes:
    - Metrics for total stories, stories in memory, and average response length
    - Pie chart showing story distribution by style
    - Bar chart showing story distribution by mode
    - Line chart showing story generation activity over the last 7 days
    - Table showing most frequently used documents
    """
    st.title("📊 Analytics Dashboard")
    
    stats = db.get_enhanced_statistics()
    
    # Basic statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Stories", stats['total_stories'])
    with col2:
        st.metric("Stories in Memory", stats['stories_in_memory'])
    with col3:
        st.metric("Average Response Length", f"{stats['avg_response_length']} chars")
    
    # Stories by style
    st.subheader("Stories by Style")
    style_df = pd.DataFrame({
        'Style': list(stats['stories_by_style'].keys()),
        'Count': list(stats['stories_by_style'].values())
    })
    fig = px.pie(style_df, values='Count', names='Style', title='Story Distribution by Style')
    st.plotly_chart(fig)
    
    # Stories by mode
    st.subheader("Stories by Mode")
    mode_df = pd.DataFrame({
        'Mode': list(stats['stories_by_mode'].keys()),
        'Count': list(stats['stories_by_mode'].values())
    })
    fig = px.bar(mode_df, x='Mode', y='Count', title='Story Distribution by Mode')
    st.plotly_chart(fig)
    
    # Last 7 days activity
    st.subheader("Last 7 Days Activity")
    days_df = pd.DataFrame({
        'Date': list(stats['stories_last_7_days'].keys()),
        'Count': list(stats['stories_last_7_days'].values())
    })
    fig = px.line(days_df, x='Date', y='Count', title='Story Generation Activity')
    st.plotly_chart(fig)
    
    # Most used documents
    st.subheader("Most Used Documents")
    docs_df = pd.DataFrame({
        'Document': list(stats['most_used_documents'].keys()),
        'Usage Count': list(stats['most_used_documents'].values())
    })
    st.dataframe(docs_df)

def story_generator_ui() -> None:
    """Display the story generator interface.
    
    This function creates a Streamlit interface for generating stories, including:
    - Style selection and customization
    - Mode selection (direct or RAG)
    - Document selection for RAG mode
    - Story generation and memory management
    """
    st.title("📖 Qwen-3B Storyteller")
    
    # Add system prompt controls
    st.sidebar.title("Story Generation Settings")
    
    # Style selection
    selected_style = st.sidebar.selectbox(
        "Select Story Style",
        list(STORY_STYLES.keys())
    )
    
    # Custom system prompt
    st.sidebar.subheader("Custom System Prompt")
    custom_prompt = st.sidebar.text_area(
        "Modify the system prompt (optional)",
        value=STORY_STYLES[selected_style],
        height=300
    )
    
    # Add mode selection
    mode = st.radio("Select generation mode:", ["Direct Generation", "RAG with Documents"])
    
    # Get available documents
    all_docs: List[str] = []
    for root, _, files in os.walk(DOCS_PATH):
        for file in files:
            if file.endswith((".txt", ".pdf", ".docx")):
                rel_path = os.path.relpath(os.path.join(root, file), DOCS_PATH)
                all_docs.append(rel_path)
    
    selected: List[str] = []
    if mode == "RAG with Documents":
        selected = st.multiselect("Select documents to include in the story generation:", all_docs)
    
    user_input = st.text_area("Describe a scene or give a prompt for storytelling:", height=150)
    add_to_memory = st.checkbox("📌 Add this story to long-term memory")

    if user_input:
        with st.spinner("Generating immersive story..."):
            try:
                answer, source_docs, now = generate_story(
                    user_input=user_input,
                    selected_style=selected_style,
                    custom_prompt=custom_prompt,
                    mode=mode,
                    selected=selected,
                    db_manager=db
                )

                if add_to_memory:
                    story_path = store_story_to_memory(answer, now)
                    story_doc = Document(page_content=answer, metadata={"source": story_path})
                    append_to_index([story_doc])

                st.markdown(f"**🧙 Story Generated:**\n\n{answer}")
                st.download_button("📄 Download Story (.txt)", data=answer.encode("utf-8"), file_name="generated_story.txt")

                if source_docs:
                    st.markdown("---")
                    st.markdown("**🧾 Source Chunks Used:**")
                    for i, doc in enumerate(source_docs):
                        st.markdown(f"**Chunk {i+1}:** `{doc.metadata.get('source', 'unknown')}`\n\n> {doc.page_content[:500]}...")
            except Exception as e:
                st.error(str(e))

def main() -> None:
    """Main entry point for the Streamlit application.
    
    This function sets up the Streamlit page configuration and handles navigation
    between different sections of the application:
    - Story Generator
    - Story Browser
    - Analytics
    """
    st.set_page_config(page_title="Qwen RAG", layout="wide")
    
    # Add navigation
    page = st.sidebar.radio("Navigation", ["Story Generator", "Story Browser", "Analytics"])
    
    if page == "Story Generator":
        story_generator_ui()
    elif page == "Story Browser":
        story_browser(db)
    else:  # Analytics
        show_analytics()

if __name__ == "__main__":
    main()
