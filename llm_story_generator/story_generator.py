"""Story generator module for the LLM Story Generator.

This module provides functionality for generating stories using a local llama.cpp server,
with support for both direct generation and RAG-based generation using document context.
"""
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.schema import Document
from typing import Dict, List, Optional, Tuple, Any, Union, Final
from datetime import datetime
import os
import hashlib
import json
import streamlit as st
import requests
import logging

from .config import (
    DOCS_PATH, INDEX_PATH, MEMORY_STORIES_PATH,
    MODEL_SETTINGS, VECTOR_STORE_SETTINGS, LOCAL_LLM_SETTINGS,
    HASH_DB_PATH
)

logger = logging.getLogger(__name__)

# Storytelling style presets
STORY_STYLES: Final[Dict[str, str]] = {
    "Creative Storyteller": """You are a creative storyteller with a deep understanding of narrative structure and character development. 
Your task is to generate engaging, immersive stories based on user prompts. 
When given a scene or prompt:
1. Create vivid descriptions that engage the senses
2. Develop characters with depth and personality
3. Maintain consistent narrative flow
4. Use appropriate pacing and tension
5. Incorporate relevant context from provided documents when in RAG mode
6. Keep the story coherent and engaging

Remember to:
- Stay in character as a storyteller
- Use descriptive language
- Create emotional resonance
- Maintain narrative consistency""",

    "One Piece Writer": """You are a masterful storyteller deeply familiar with the world of One Piece, created by Eiichiro Oda. Your task is to write engaging, original short stories set within the One Piece universe, introducing new characters that seamlessly fit into its world.

The stories must reflect the tone, themes, and worldbuilding style of One Piece, including:

Grand adventures, camaraderie, and humor

Pirate crews, Marines, bounty hunters, and Revolutionary Army dynamics

Devil Fruits and Haki systems

Unique islands and cultures across the Grand Line and beyond

Creative powers, exaggerated personalities, and heartfelt motivations

Character Creation Guidelines:

Design characters with distinct quirks, dreams, and backstories.

Assign them fitting roles (e.g., pirate captain, Marine scientist, revolutionary agent, bounty hunter).

Include Devil Fruit abilities (if applicable), creative weapons, or Haki types.

Narrative Requirements:

Each short story should be 400 to 800 words.

Introduce the new character naturally within an exciting or emotional scene.

Capture the charm, humor, and emotional depth typical of One Piece arcs.

Avoid using canon characters directly; brief references (e.g., "a pirate known as Straw Hat") are acceptable.

Prioritize creativity, emotional resonance, and narrative immersion. Keep the tone accessible for fans of the anime and manga, with a flair for imaginative action and heartfelt character development."""
}

def hash_file(filepath: str) -> str:
    """Calculate MD5 hash of a file.
    
    Args:
        filepath: Path to the file to hash.
    
    Returns:
        str: MD5 hash of the file contents.
    """
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def load_documents(path: str, selected_files: Optional[List[str]] = None) -> List[Document]:
    """Load documents from the specified path.
    
    Args:
        path: Base path to search for documents.
        selected_files: Optional list of specific files to load.
    
    Returns:
        List[Document]: List of loaded documents.
    """
    docs: List[Document] = []
    hashes: Dict[str, str] = {}
    hash_db = load_hash_db()
    for root, _, files in os.walk(path):
        for file in files:
            if not file.endswith((".txt", ".pdf", ".docx")):
                continue
            rel_path = os.path.relpath(os.path.join(root, file), path)
            if selected_files and rel_path not in selected_files:
                continue

            full_path = os.path.join(path, rel_path)
            if not os.path.isfile(full_path):
                continue

            file_hash = hash_file(full_path)
            if rel_path in hash_db and hash_db[rel_path] == file_hash:
                continue

            if file.endswith(".txt"):
                docs.extend(TextLoader(full_path).load())
            elif file.endswith(".pdf"):
                docs.extend(PyPDFLoader(full_path).load())
            elif file.endswith(".docx"):
                docs.extend(Docx2txtLoader(full_path).load())

            hashes[rel_path] = file_hash

    update_hash_db(hashes)
    return docs

def load_hash_db() -> Dict[str, str]:
    """Load the hash database from disk.
    
    Returns:
        Dict[str, str]: Dictionary mapping file paths to their hashes.
    """
    if os.path.exists(HASH_DB_PATH):
        with open(HASH_DB_PATH, "r") as f:
            return json.load(f)
    return {}

def update_hash_db(new_hashes: Dict[str, str]) -> None:
    """Update the hash database with new file hashes.
    
    Args:
        new_hashes: Dictionary of new file hashes to add/update.
    """
    hash_db = load_hash_db()
    hash_db.update(new_hashes)
    with open(HASH_DB_PATH, "w") as f:
        json.dump(hash_db, f)

def append_to_index(new_docs: List[Document]) -> FAISS:
    """Append new documents to the vector store index.
    
    Args:
        new_docs: List of documents to append.
    
    Returns:
        FAISS: Updated vector store instance.
    
    Raises:
        Exception: If appending documents fails.
    """
    if not new_docs:
        return load_vectordb()
    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=VECTOR_STORE_SETTINGS["chunk_size"],
            chunk_overlap=VECTOR_STORE_SETTINGS["chunk_overlap"]
        )
        chunks = splitter.split_documents(new_docs)
        embedder = SentenceTransformerEmbeddings(
            model_name=VECTOR_STORE_SETTINGS["embedding_model"]
        )
        if os.path.exists(INDEX_PATH):
            vectordb = FAISS.load_local(INDEX_PATH, embedder, allow_dangerous_deserialization=True)
            vectordb.add_documents(chunks)
        else:
            vectordb = FAISS.from_documents(chunks, embedder)
        vectordb.save_local(INDEX_PATH)
        return vectordb
    except Exception as e:
        logger.error(f"Failed to append documents to index: {str(e)}")
        raise

def load_vectordb() -> FAISS:
    """Load the vector store from disk.
    
    Returns:
        FAISS: Vector store instance.
    
    Raises:
        Exception: If loading the vector store fails.
    """
    try:
        embedder = SentenceTransformerEmbeddings(
            model_name=VECTOR_STORE_SETTINGS["embedding_model"]
        )
        return FAISS.load_local(INDEX_PATH, embedder, allow_dangerous_deserialization=True)
    except Exception as e:
        logger.error(f"Failed to load vector database: {str(e)}")
        raise

def load_llm(system_prompt: Optional[str] = None) -> ChatOpenAI:
    """Load the local LLM model through llama.cpp server.
    
    This function initializes a connection to the local llama.cpp server using
    LangChain's OpenAI-compatible interface.
    
    Args:
        system_prompt: Optional custom system prompt to use.
    
    Returns:
        ChatOpenAI: Initialized LLM instance.
    
    Raises:
        Exception: If loading the LLM fails.
    """
    try:
        # Validate server connection first
        base_url = LOCAL_LLM_SETTINGS["base_url"]
        logger.info(f"Attempting to connect to local LLM server at {base_url}")
        
        try:
            # Use the models endpoint to check server availability
            response = requests.get(f"{base_url}/models", timeout=5)
            if response.status_code != 200:
                raise ConnectionError(f"Server returned status code {response.status_code}")
            
            # Check if our model is available
            models_data = response.json()
            available_models = [model.get("id") for model in models_data.get("data", [])]
            if LOCAL_LLM_SETTINGS["model"] not in available_models:
                raise ConnectionError(f"Model {LOCAL_LLM_SETTINGS['model']} not found in available models: {available_models}")
                
            logger.info(f"Server connection successful. Available models: {available_models}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to local LLM server: {str(e)}")
        except json.JSONDecodeError as e:
            raise ConnectionError(f"Invalid server response format: {str(e)}")
        
        # Create LangChain OpenAI wrapper for local llama.cpp server
        llm = ChatOpenAI(
            model_name=MODEL_SETTINGS["model_name"],
            temperature=MODEL_SETTINGS["temperature"],
            max_tokens=MODEL_SETTINGS["max_tokens"],
            openai_api_key=LOCAL_LLM_SETTINGS["api_key"],
            openai_api_base=LOCAL_LLM_SETTINGS["base_url"],
            model=LOCAL_LLM_SETTINGS["model"],
            streaming=False,  # Disable streaming for better compatibility
            request_timeout=300,  # Increase timeout for larger responses
            max_retries=5  # Add retries for better reliability
        )
        
        logger.info("Successfully initialized connection to local LLM server")
        return llm
    except Exception as e:
        logger.error(f"Failed to load local LLM: {str(e)}")
        raise

def store_story_to_memory(story_text: str, timestamp: str) -> str:
    """Store a generated story to memory.
    
    Args:
        story_text: The story text to store.
        timestamp: Timestamp for the story.
    
    Returns:
        str: Path to the stored story file.
    
    Raises:
        Exception: If storing the story fails.
    """
    try:
        filename = f"story_{timestamp.replace(':', '-').replace('T','_')}.txt"
        path = os.path.join(MEMORY_STORIES_PATH, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"[Time: {timestamp}]\n\n{story_text}\n")
        logger.info(f"Story stored to memory: {path}")
        return path
    except Exception as e:
        logger.error(f"Failed to store story to memory: {str(e)}")
        raise

def generate_story(
    user_input: str,
    selected_style: str,
    custom_prompt: str,
    mode: str,
    selected: List[str],
    db_manager: Any
) -> Tuple[str, List[Document], str]:
    """Generate a story based on user input and selected parameters.
    
    This function handles both direct story generation and RAG-based generation
    using document context. It supports different storytelling styles and modes.
    
    Args:
        user_input: The user's input prompt or scene description.
        selected_style: The selected storytelling style (e.g., "Creative Storyteller").
        custom_prompt: Custom system prompt to use for generation.
        mode: Generation mode ("Direct Generation" or "RAG with Documents").
        selected: List of selected document filenames for RAG mode.
        db_manager: Database manager instance for story operations.
    
    Returns:
        Tuple[str, List[Document], str]: A tuple containing:
            - The generated story text
            - List of source documents used (if any)
            - Timestamp of generation
    
    Raises:
        Exception: If story generation fails or if required documents are not found.
    """
    try:
        logger.info(f"Starting story generation with mode: '{mode}'")
        timestamp = datetime.now().isoformat()
        system_prompt = custom_prompt or STORY_STYLES.get(selected_style, STORY_STYLES["Creative Storyteller"])
        
        # Initialize LLM with system prompt
        llm = load_llm(system_prompt)
        
        # Check if we're in direct mode
        mode = mode.strip().lower()  # Normalize the mode string
        logger.info(f"Normalized mode: '{mode}'")
        
        if mode == "direct generation":
            logger.info("Entering direct generation mode")
            try:
                # Direct generation without RAG
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
                logger.info("Sending request to LLM")
                response = llm.invoke(messages)
                
                # Handle different response types
                if hasattr(response, 'content'):
                    story = response.content
                elif isinstance(response, str):
                    story = response
                else:
                    story = str(response)
                
                logger.info("Successfully generated story in direct mode")
                
                # Store story in database
                db_manager.add_story(
                    prompt=user_input,
                    response=story,
                    system_prompt=system_prompt,
                    style=selected_style,
                    mode=mode
                )
                
                # Store story to memory
                store_story_to_memory(story, timestamp)
                
                return story, [], timestamp
            except Exception as e:
                logger.error(f"Failed to generate story in direct mode: {str(e)}")
                raise ValueError(f"Failed to generate story: {str(e)}")
        
        # RAG mode
        logger.info("Entering RAG mode")
        if not selected:
            logger.error("No documents selected for RAG mode")
            raise ValueError("No documents selected for RAG mode")
            
        docs = load_documents(DOCS_PATH, selected)
        if not docs:
            logger.error("No documents available for RAG mode")
            raise ValueError("No documents available for RAG mode")
        
        vectordb = append_to_index(docs)
        
        chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectordb.as_retriever(
                search_kwargs={"k": VECTOR_STORE_SETTINGS["k"]}
            )
        )
        
        result = chain({"question": user_input})
        story = result["answer"]
        sources = result["sources"]
        
        # Store story in database
        db_manager.add_story(
            prompt=user_input,
            response=story,
            system_prompt=system_prompt,
            style=selected_style,
            mode=mode
        )
        
        # Store story to memory
        store_story_to_memory(story, timestamp)
        
        return story, sources, timestamp
    except Exception as e:
        logger.error(f"Failed to generate story: {str(e)}")
        raise 