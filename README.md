![ai-knowledge-graph-example](https://github.com/robert-mcdermott/ai-knowledge-graph/blob/main/data/ai-knowledge-graph-example.png)

# AI Powered Knowledge Graph Generator

This system takes text documents, extracts knowledge in the form of Subject-Predicate-Object (SPO) triplets, and visualizes the relationships as an interactive knowledge graph.

## Features

- **Text Chunking**: Automatically splits large documents into manageable chunks for processing
- **Knowledge Extraction**: Uses AI to identify entities and their relationships
- **Entity Standardization**: Ensures consistent entity naming across document chunks
- **Relationship Inference**: Discovers additional relationships between disconnected parts of the graph
- **Interactive Visualization**: Creates a beautiful, interactive graph visualization

## Requirements

- Python 3.11+
- Required packages (install using `pip install -r requirements.txt` or `uv sync`)

## Quick Start

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your settings in `config.toml`
4. Run the system:

```bash
python generate-graph.py --input your_text_file.txt --output knowledge_graph.html
```

Or with UV:

```bash
uv run generate-graph.py --input your_text_file.txt --output knowledge_graph.html
```
Or installing and using as a module:

```bash
pip install --upgrade -e .
generate-graph.py --input your_text_file.txt --output knowledge_graph.html
```

## Configuration

The system can be configured using the `config.toml` file:

```toml
[llm]
model = "gemma3"
api_key = "sk-1234"
base_url = "http://localhost:11434/v1/chat/completions"
max_tokens = 8192
temperature = 0.2

[chunking]
chunk_size = 200  # Number of words per chunk
overlap = 20      # Number of words to overlap between chunks

[standardization]
enabled = true            # Enable entity standardization
use_llm_for_entities = true  # Use LLM for additional entity resolution

[inference]
enabled = true             # Enable relationship inference
use_llm_for_inference = true  # Use LLM for relationship inference
apply_transitive = true    # Apply transitive inference rules
```

## Command Line Options

- `--input FILE`: Input text file to process
- `--output FILE`: Output HTML file for visualization (default: knowledge_graph.html)
- `--config FILE`: Path to config file (default: config.toml)
- `--debug`: Enable debug output with raw LLM responses
- `--no-standardize`: Disable entity standardization
- `--no-inference`: Disable relationship inference
- `--test`: Generate sample visualization using test data

### Usage message (--help)

```bash
generate-graph --help
usage: generate-graph [-h] [--test] [--config CONFIG] [--output OUTPUT] [--input INPUT] [--debug] [--no-standardize] [--no-inference]

Knowledge Graph Generator and Visualizer

options:
  -h, --help        show this help message and exit
  --test            Generate a test visualization with sample data
  --config CONFIG   Path to configuration file
  --output OUTPUT   Output HTML file path
  --input INPUT     Path to input text file (required unless --test is used)
  --debug           Enable debug output (raw LLM responses and extracted JSON)
  --no-standardize  Disable entity standardization
  --no-inference    Disable relationship inference
```


## How It Works

1. **Chunking**: The document is split into overlapping chunks to fit within the LLM's context window
2. **First Pass - SPO Extraction**: 
   - Each chunk is processed by the LLM to extract Subject-Predicate-Object triplets
   - Implemented in the `process_with_llm` function
   - The LLM identifies entities and their relationships within each text segment
   - Results are collected across all chunks to form the initial knowledge graph
3. **Second Pass - Entity Standardization**:
   - Basic standardization through text normalization
   - Optional LLM-assisted entity alignment (controlled by `standardization.use_llm_for_entities` config)
   - When enabled, the LLM reviews all unique entities from the graph and identifies groups that refer to the same concept
   - This resolves cases where the same entity appears differently across chunks (e.g., "AI", "artificial intelligence", "AI system")
   - Standardization helps create a more coherent and navigable knowledge graph
4. **Third Pass - Relationship Inference**:
   - Automatic inference of transitive relationships
   - Optional LLM-assisted inference between disconnected graph components (controlled by `inference.use_llm_for_inference` config)
   - When enabled, the LLM analyzes representative entities from disconnected communities and infers plausible relationships
   - This reduces graph fragmentation by adding logical connections not explicitly stated in the text
   - Both rule-based and LLM-based inference methods work together to create a more comprehensive graph
5. **Visualization**: An interactive HTML visualization is generated using the PyVis library

Both the second and third passes are optional and can be disabled in the configuration to minimize LLM usage or control these processes manually.

## Visualization Features

- **Color-coded Communities**: Node colors represent different communities
- **Node Size**: Nodes sized by importance (degree, betweenness, eigenvector centrality)
- **Relationship Types**: Original relationships shown as solid lines, inferred relationships as dashed lines
- **Interactive Controls**: Zoom, pan, hover for details, filtering and physics controls
- **Light (default) and Dark mode themes.

## Project Layout

```
.
├── config.toml                     # Main configuration file for the system
├── generate-graph.py               # Entry point when run directly as a script
├── pyproject.toml                  # Python project metadata and build configuration
├── requirements.txt                # Python dependencies for 'pip' users
├── uv.lock                         # Python dependencies for 'uv' users
└── src/                            # Source code
    ├── generate_graph.py           # Main entry point script when run as a module
    └── knowledge_graph/            # Core package
        ├── __init__.py             # Package initialization
        ├── config.py               # Configuration loading and validation
        ├── entity_standardization.py # Entity standardization algorithms
        ├── llm.py                  # LLM interaction and response processing
        ├── main.py                 # Main program flow and orchestration
        ├── text_utils.py           # Text processing and chunking utilities
        ├── visualization.py        # Knowledge graph visualization generator
        └── templates/              # HTML templates for visualization
            └── graph_template.html # Base template for interactive graph
```

