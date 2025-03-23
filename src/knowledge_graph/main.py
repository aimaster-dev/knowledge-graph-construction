"""
Knowledge Graph Generator and Visualizer main module.
"""
import argparse
import json
import os
import sys

# Add the parent directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.knowledge_graph.config import load_config
from src.knowledge_graph.llm import call_llm, extract_json_from_text
from src.knowledge_graph.visualization import visualize_knowledge_graph, sample_data_visualization
from src.knowledge_graph.text_utils import chunk_text

def process_with_llm(config, input_text):
    """
    Process input text with LLM to extract triples.
    
    Args:
        config: Configuration dictionary
        input_text: Text to analyze
        
    Returns:
        List of extracted triples or None if processing failed
    """
    # Choose which system prompt to use
    system_prompt = config["prompts"]["system_prompt"]
    user_prompt = config["prompts"]["user_prompt"]
    user_prompt += f"context: ```\n{input_text}```\n" 

    # LLM configuration
    model = config["llm"]["model"]
    api_key = config["llm"]["api_key"]
    max_tokens = config["llm"]["max_tokens"]
    temperature = config["llm"]["temperature"]
    
    # Process with LLM
    metadata = {}
    response = call_llm(model, user_prompt, api_key, system_prompt, max_tokens, temperature)
    
    # Print raw response for debugging
    print("Raw LLM response:")
    print(response)
    print("\n---\n")
    
    # Extract JSON from the response
    result = extract_json_from_text(response)
    
    if result:
        # Add metadata to each item
        result = [dict(item, **metadata) for item in result]
        print("Extracted JSON:")
        print(json.dumps(result, indent=2))  # Pretty print the JSON
        return result
    else:
        print("\n\nERROR ### Could not extract valid JSON from response: ", response, "\n\n")
        return None

def process_text_in_chunks(config, full_text):
    """
    Process a large text by breaking it into chunks with overlap,
    and then processing each chunk separately.
    
    Args:
        config: Configuration dictionary
        full_text: The complete text to process
    
    Returns:
        List of all extracted triples from all chunks
    """
    # Get chunking parameters from config
    chunk_size = config.get("chunking", {}).get("chunk_size", 500)
    overlap = config.get("chunking", {}).get("overlap", 50)
    
    # Split text into chunks
    text_chunks = chunk_text(full_text, chunk_size, overlap)
    
    print(f"Processing text in {len(text_chunks)} chunks (size: {chunk_size} words, overlap: {overlap} words)")
    
    # Process each chunk
    all_results = []
    for i, chunk in enumerate(text_chunks):
        print(f"\nProcessing chunk {i+1}/{len(text_chunks)} ({len(chunk.split())} words)")
        
        # Process the chunk with LLM
        chunk_results = process_with_llm(config, chunk)
        
        if chunk_results:
            # Add chunk information to each triple
            for item in chunk_results:
                item["chunk"] = i + 1
            
            # Add to overall results
            all_results.extend(chunk_results)
        else:
            print(f"Warning: Failed to extract triples from chunk {i+1}")
    
    print(f"\nExtracted a total of {len(all_results)} triples from all chunks")
    return all_results

def main():
    """Main entry point for the knowledge graph generator."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Knowledge Graph Generator and Visualizer')
    parser.add_argument('--test', action='store_true', help='Generate a test visualization with sample data')
    parser.add_argument('--config', type=str, default='config.toml', help='Path to configuration file')
    parser.add_argument('--output', type=str, default='knowledge_graph.html', help='Output HTML file path')
    parser.add_argument('--input', type=str, required=True, help='Path to input text file (required)')
    
    args = parser.parse_args()
    
    # If test flag is provided, generate a sample visualization
    if args.test:
        sample_data_visualization(args.output)
        return
    
    # Normal processing continues below
    # Load configuration
    config = load_config(args.config)
    if not config:
        print(f"Failed to load configuration from {args.config}. Exiting.")
        return
    
    # Load input text from file
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            input_text = f.read()
        print(f"Using input text from file: {args.input}")
    except Exception as e:
        print(f"Error reading input file {args.input}: {e}")
        return
    
    # Process text in chunks
    result = process_text_in_chunks(config, input_text)
    
    if result:
        # Visualize the knowledge graph
        stats = visualize_knowledge_graph(result, args.output)
        print("\nKnowledge Graph Statistics:")
        print(f"Nodes: {stats['nodes']}")
        print(f"Edges: {stats['edges']}")
        print(f"Communities: {stats['communities']}")
        
        # Provide command to open the visualization in a browser
        print("\nTo view the visualization, open the following file in your browser:")
        print(f"file://{os.path.abspath(args.output)}")
    else:
        print("Knowledge graph generation failed due to errors in LLM processing.")

if __name__ == "__main__":
    main() 