"""Setup configuration for the LLM Story Generator package.

This module configures the package installation settings, including dependencies
and Python version requirements.
"""
from typing import List
from setuptools import setup, find_packages

setup(
    name="llm_story_generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "langchain",
        "faiss-cpu",
        "sentence-transformers",
        "pandas",
        "plotly",
        "requests"
    ],
    python_requires=">=3.8",
) 