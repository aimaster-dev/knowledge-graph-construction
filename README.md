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
uv run generate-graph.py [options]
```

### Using standard Python

```bash
python generate-graph.py [options]
```

### After installation

```bash
generate-graph [options]
```

## Command Line Options

- `--test`: Generate a test visualization with sample data
- `--config`: Path to configuration file (default: `config.toml`)
- `--output`: Output HTML file path (default: `knowledge_graph.html`)
- `--input`: Path to input text file (overrides the input in config file)

## Configuration

The tool is configured using a TOML file (default: `config.toml`). The configuration file contains:

- LLM settings (model, API key, etc.)
- Input data (can be overridden with the `--input` command line option)
- Prompts for knowledge extraction

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