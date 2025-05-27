# LLM Story Generator

A powerful tool for generating stories using Large Language Models (LLMs) with Retrieval-Augmented Generation (RAG) capabilities.

**Author:** Your Name  
**Repository:** https://github.com/yourusername/llm-story-generator

## Features

- Story generation using LLMs
- Document-based context retrieval
- Vector store for efficient document search
- Story management and analytics
- Web interface for story browsing and export
- Comprehensive test coverage

## Requirements

- Python 3.10+

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/llm-story-generator.git
cd llm-story-generator
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install development dependencies (optional):
```bash
pip install ruff pytest pytest-cov mypy types-requests types-PyPDF2
```

## Usage

1. Start the LLM server using Docker Compose:
```bash
docker-compose up -d
```

2. Run the story generator:
```bash
python -m llm_story_generator
```

3. Access the web interface at `http://localhost:8501`

## Development

- Run tests:
```bash
pytest
```

- Run type checking (strict type hints enforced):
```bash
mypy .
```

- Run linting and formatting (Ruff):
```bash
ruff check .
```

- All code must include Google-style docstrings and type hints as per project rules.

## Project Structure

```
llm_story_generator/
├── llm_story_generator/
│   ├── __init__.py
│   ├── config.py
│   ├── db_manager.py
│   ├── story_browser.py
│   └── story_generator.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_db_manager.py
│   ├── test_db_manager_new.py
│   ├── test_story_generator.py
│   └── test_story_generator_new.py
├── compose.yaml
├── pyproject.toml
├── requirements.txt
├── requirements-test.txt
├── schema.sql
└── setup.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 