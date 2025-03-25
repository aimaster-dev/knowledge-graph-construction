# AI Knowledge Graph Generator

This system takes text documents, extracts knowledge in the form of Subject-Predicate-Object (SPO) triplets, and visualizes the relationships as an interactive knowledge graph.

## Features

- **Text Chunking**: Automatically splits large documents into manageable chunks for processing
- **Knowledge Extraction**: Uses AI to identify entities and their relationships
- **Entity Standardization**: Ensures consistent entity naming across document chunks
- **Relationship Inference**: Discovers additional relationships between disconnected parts of the graph
- **Interactive Visualization**: Creates a beautiful, interactive graph visualization

## Requirements

- Python 3.8+
- Required packages (install using `pip install -r requirements.txt`)

## Quick Start

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your settings in `config.toml`
4. Run the system:

```bash
python generate-graph.py --input your_text_file.txt --output knowledge_graph.html
```

## Configuration

The system can be configured using the `config.toml` file:

```toml
[llm]
model = "claude-3.5-sonnet-v2"  # or other models like "gpt4o", "gemma3"
api_key = "your-api-key"
base_url = "http://localhost:4000/v1/chat/completions"  # Change as needed
max_tokens = 8096
temperature = 0.8

[chunking]
chunk_size = 500  # Number of words per chunk
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

## How It Works

1. **Chunking**: The document is split into overlapping chunks to fit within the LLM's context window
2. **SPO Extraction**: Each chunk is processed to extract Subject-Predicate-Object triplets
3. **Entity Standardization**:
   - Basic standardization through text normalization
   - Optional LLM-assisted entity alignment
4. **Relationship Inference**:
   - Automatic inference of transitive relationships
   - Optional LLM-assisted inference between disconnected graph components
5. **Visualization**: An interactive HTML visualization is generated using the PyVis library

## Visualization Features

- **Color-coded Communities**: Node colors represent different communities
- **Node Size**: Nodes sized by importance (degree, betweenness, eigenvector centrality)
- **Relationship Types**: Original relationships shown as solid lines, inferred relationships as dashed lines
- **Interactive Controls**: Zoom, pan, hover for details, and physics controls

## Customization

- Edit prompts in `config.toml` to customize knowledge extraction behavior
- Modify visualization settings in `src/knowledge_graph/visualization.py`
- Adjust entity standardization and inference parameters in `config.toml`

## License

[License Information]