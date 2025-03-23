# AI Knowledge Graph Generator and Visualizer

This tool extracts knowledge triples (Subject-Predicate-Object relationships) from text using an LLM and visualizes them as an interactive knowledge graph with community detection.

## Features

- **LLM-based Knowledge Extraction**: Uses a local LLM through Ollama to extract knowledge triples from text
- **Interactive Visualization**: Creates an interactive HTML visualization of the knowledge graph
- **Community Detection**: Identifies and colors node communities
- **Importance Weighting**: Sizes nodes based on their importance in the graph
- **Physics Simulation**: Interactive physics-based layout with stabilization controls

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd ai-knowlege-graph
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Make sure you have [Ollama](https://ollama.ai/) installed and running locally.

## Usage

### Configuration

Edit the `config.toml` file to configure:
- The input text to analyze
- The LLM to use (via Ollama)
- System and user prompts for the LLM

### Run the Graph Generator

Run the script to extract knowledge and generate the visualization:

```
python generate-graph.py
```

The visualization will be saved as `knowledge_graph.html` in the current directory.

### Test Visualization

To test the visualization with sample data (without LLM processing):

```
python generate-graph.py --test
```

This will generate a `sample_knowledge_graph.html` file.

## Visualization Features

The generated HTML visualization includes:
- Interactive node movement
- Node coloring by community
- Node sizing by importance (calculated based on centrality)
- Edge labels showing relationships
- Physics controls (toggle physics, stabilize layout)
- Community color legend

## How it Works

1. **Knowledge Extraction**: The tool sends the input text to the LLM with a prompt requesting S-P-O (Subject-Predicate-Object) triples.
2. **JSON Parsing**: The LLM response is parsed to extract the JSON array of triples.
3. **Graph Construction**: A directed graph is built using NetworkX with nodes and edges from the triples.
4. **Community Detection**: Communities are identified to color-code related nodes.
5. **Importance Calculation**: Node importance is calculated based on centrality metrics.
6. **Visualization**: The graph is visualized as an interactive HTML page using PyVis.

## Modifying the Code

- **Prompt Engineering**: Edit the prompts in `config.toml` to change how the LLM extracts knowledge.
- **Visualization Settings**: Modify the visualization parameters in the code (colors, physics, layout).
- **Community Detection**: The code currently uses a degree-based community detection fallback, but will try to use the Louvain method if available.

## Example Output

When you open the HTML file in a browser, you'll see an interactive graph with:
- Nodes representing entities (colored by community)
- Directed edges showing relationships
- Hover tooltips displaying node information
- Controls for manipulating the physics simulation
