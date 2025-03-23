# AI Knowledge Graph Generator

A tool that takes text input and generates an interactive knowledge graph visualization.

## Overview

This tool uses a large language model (LLM) to extract subject-predicate-object relationships from text, and then visualizes these relationships as a knowledge graph. The visualization is interactive and allows for exploring connections between concepts.

## Installation

1. Clone this repository
2. Make sure you have Python 3.12+ installed
3. Install dependencies:

```bash
pip install -e .
```

## Usage

You can run the tool in different ways:

### Using uv run (recommended)

```bash
uv run generate-graph.py --input your_input_file.txt [options]
```

### Using standard Python

```bash
python generate-graph.py --input your_input_file.txt [options]
```

### After installation

```bash
generate-graph --input your_input_file.txt [options]
```

## Command Line Options

- `--input`: Path to input text file (required)
- `--test`: Generate a test visualization with sample data
- `--config`: Path to configuration file (default: `config.toml`)
- `--output`: Output HTML file path (default: `knowledge_graph.html`)

## Configuration

The tool is configured using a TOML file (default: `config.toml`). The configuration file contains:

- LLM settings (model, API key, etc.)
- Chunking settings (for processing large input files)
- Prompts for knowledge extraction

### Chunking Configuration

For processing large input files, the tool splits the text into smaller chunks with overlap:

```toml
[chunking]
chunk_size = 500  # Number of words per chunk
overlap = 50      # Number of words to overlap between chunks
```

These settings help ensure that large documents are properly analyzed without exceeding LLM context limits.

## Project Structure

```
├── generate-graph.py         # Root entry point script
├── src/                      # Source code directory
│   ├── generate_graph.py     # Module entry point script
│   └── knowledge_graph/      # Main package
│       ├── __init__.py       # Package initialization 
│       ├── main.py           # Main logic and CLI interface
│       ├── config.py         # Configuration handling
│       ├── llm.py            # LLM interaction utilities
│       └── visualization.py  # Graph visualization utilities
```

## License

See [LICENSE](LICENSE) file for details.