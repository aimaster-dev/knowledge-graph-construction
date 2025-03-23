import requests
import json
import re
import tomli  # For reading TOML files
import networkx as nx
from pyvis.network import Network
import random
import os
import sys
import argparse

def load_config(config_file="config.toml"):
    """Load configuration from TOML file"""
    try:
        with open(config_file, "rb") as f:
            return tomli.load(f)
    except Exception as e:
        print(f"Error loading config file: {e}")
        return None

def visualize_knowledge_graph(triples, output_file="knowledge_graph.html"):
    """
    Create and visualize a knowledge graph from subject-predicate-object triples.
    
    Args:
        triples: List of dictionaries with 'subject', 'predicate', and 'object' keys
        output_file: HTML file to save the visualization
    """
    if not triples:
        print("Warning: No triples provided for visualization")
        return {"nodes": 0, "edges": 0, "communities": 0}
        
    print(f"Processing {len(triples)} triples for visualization")
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Dictionary to store node groups for community visualization
    node_communities = {}
    
    # Set of all unique nodes
    all_nodes = set()
    
    # Add all subjects and objects as nodes
    for triple in triples:
        subject = triple["subject"]
        obj = triple["object"]
        all_nodes.add(subject)
        all_nodes.add(obj)
    
    print(f"Found {len(all_nodes)} unique nodes")
    
    # Create an undirected graph for community detection and centrality measures
    G_undirected = nx.Graph()
    
    for triple in triples:
        G_undirected.add_edge(triple["subject"], triple["object"])
    
    # Calculate node centrality metrics to determine importance
    # Betweenness centrality - nodes that bridge communities are more important
    betweenness = nx.betweenness_centrality(G_undirected)
    # Degree centrality - nodes with more connections are more important
    degree = dict(G_undirected.degree())
    # Eigenvector centrality - nodes connected to high-value nodes are more important
    try:
        eigenvector = nx.eigenvector_centrality(G_undirected, max_iter=1000)
    except:
        # If eigenvector calculation fails (can happen with certain graph structures)
        eigenvector = {node: 0.5 for node in all_nodes}
    
    # Try to use NetworkX community detection, fallback to simple degree-based approach
    try:
        # Attempt to detect communities using Louvain method
        import community as community_louvain
        partition = community_louvain.best_partition(G_undirected)
        node_communities = partition
        community_count = len(set(partition.values()))
        print(f"Detected {community_count} communities using Louvain method")
    except:
        # Fallback: assign community IDs based on degree for simplicity
        for node in all_nodes:
            node_degree = G_undirected.degree(node) if node in G_undirected else 0
            # Ensure we have at least 0 as a community ID
            community_id = max(0, node_degree) % 8  # Using modulo 8 to limit number of colors
            node_communities[node] = community_id
        community_count = len(set(node_communities.values()))
        print(f"Using degree-based communities ({community_count} communities)")
    
    # Define colors for communities - these are standard colorblind-friendly colors
    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33', '#a65628', '#f781bf']
    
    # Calculate node size based on importance (normalized for better visuals)
    max_betweenness = max(betweenness.values()) if betweenness else 1
    max_degree = max(degree.values()) if degree else 1
    max_eigenvector = max(eigenvector.values()) if eigenvector else 1
    
    node_sizes = {}
    for node in all_nodes:
        # Normalize and combine metrics with weights
        degree_norm = degree.get(node, 1) / max_degree
        betweenness_norm = betweenness.get(node, 0) / max_betweenness if max_betweenness > 0 else 0
        eigenvector_norm = eigenvector.get(node, 0) / max_eigenvector if max_eigenvector > 0 else 0
        
        # Calculate a weighted importance score (adjust weights as needed)
        importance = 0.5 * degree_norm + 0.3 * betweenness_norm + 0.2 * eigenvector_norm
        
        # Scale node size - ensure minimum size and reasonable maximum
        node_sizes[node] = 10 + (20 * importance)  # Size range from 10 to 30
    
    # Add nodes to the graph with community colors and sizes
    for node in all_nodes:
        community = node_communities[node]
        G.add_node(
            node, 
            color=colors[community % len(colors)],  # Ensure we don't go out of bounds
            label=node,  # Explicit label
            title=f"{node}<br>Connections: {degree.get(node, 0)}",  # Tooltip with info
            size=node_sizes[node]
        )
    
    # Add edges with predicates as labels
    for triple in triples:
        G.add_edge(
            triple["subject"], 
            triple["object"], 
            title=triple["predicate"],
            label=triple["predicate"],
            arrows="to",   # Add arrow direction
            width=1        # Edge width
        )
    
    # Create a PyVis network with explicit configuration
    net = Network(
        height="750px", 
        width="100%", 
        directed=True,
        notebook=False
    )
    
    # Dump some debug info
    print(f"Nodes in NetworkX graph: {G.number_of_nodes()}")
    print(f"Edges in NetworkX graph: {G.number_of_edges()}")
    
    # Add nodes and edges from NetworkX graph - do this explicitly for better control
    for node_id in G.nodes():
        node_data = G.nodes[node_id]
        net.add_node(
            node_id, 
            color=node_data.get('color', '#4daf4a'),
            label=str(node_id),  # Ensure label is a string
            title=str(node_data.get('title', node_id)),  # Ensure title is a string
            shape="dot",
            size=node_data.get('size', 10)
        )
    
    for edge in G.edges(data=True):
        source, target, data = edge
        net.add_edge(
            source, 
            target, 
            title=data.get('title', ''),
            label=data.get('label', ''),
            arrows="to"
        )
    
    # Configure physics for better visualization
    physics_options = {
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {
            "gravitationalConstant": -50,
            "centralGravity": 0.01,
            "springLength": 100,
            "springConstant": 0.08
        },
        "stabilization": {
            "iterations": 200  # Increased for better layout
        }
    }
    
    # Apply configuration options
    options = {
        "physics": physics_options,
        "edges": {
            "color": {"inherit": True},
            "font": {"size": 12},
            "smooth": False  # Straight edges are easier to read
        },
        "nodes": {
            "font": {"size": 14, "face": "Tahoma"},
            "scaling": {"min": 10, "max": 30}  # Ensure nodes are visible
        },
        "interaction": {
            "hover": True,
            "navigationButtons": True,
            "keyboard": True,
            "tooltipDelay": 200
        },
        "layout": {
            "improvedLayout": True
        }
    }
    
    # Set all options in one go with proper JSON
    net.set_options(json.dumps(options))
    
    # Add custom HTML template with controls and legend
    html_template = """
    <div class="card" style="width: 100%">
        <div id="graph-controls" style="margin: 10px; display: flex; justify-content: space-between;">
            <div>
                <button onclick="togglePhysics()" class="btn btn-primary">Toggle Physics</button>
                <button onclick="stabilizeNetwork()" class="btn btn-secondary">Stabilize</button>
            </div>
            <div>
                <span style="margin-right: 15px;"><strong>Communities:</strong></span>
                <span style="background-color: #e41a1c; width: 20px; height: 20px; display: inline-block; margin-right: 5px;"></span>
                <span style="background-color: #377eb8; width: 20px; height: 20px; display: inline-block; margin-right: 5px;"></span>
                <span style="background-color: #4daf4a; width: 20px; height: 20px; display: inline-block; margin-right: 5px;"></span>
                <span style="background-color: #984ea3; width: 20px; height: 20px; display: inline-block; margin-right: 5px;"></span>
                <span style="background-color: #ff7f00; width: 20px; height: 20px; display: inline-block; margin-right: 5px;"></span>
            </div>
        </div>
        <div id="mynetwork" class="card-body"></div>
    </div>
    
    <script>
    function togglePhysics() {
        if (network.physics.options.enabled) {
            network.physics.stopSimulation();
            network.setOptions({physics: {enabled: false}});
        } else {
            network.setOptions({physics: {enabled: true}});
            network.startSimulation();
        }
    }
    
    function stabilizeNetwork() {
        network.stabilize(100);
    }
    
    // Once network is loaded, add info box
    network.once("stabilizationIterationsDone", function() {
        // Auto-stabilize after initial load
        setTimeout(function() {
            network.stopSimulation();
        }, 1000);
    });
    </script>
    """
    
    # Save the network as HTML and then append our custom controls
    net.save_graph(output_file)
    
    # Read the generated HTML
    with open(output_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Add our custom controls by replacing the div with our template
    html = html.replace('<div id="mynetwork" class="card-body"></div>', html_template)
    
    # Fix the duplicate title issue
    # Remove the default PyVis header
    html = re.sub(r'<center>\s*<h1>.*?</h1>\s*</center>', '', html)
    
    # Replace the other h1 with our enhanced title
    html = html.replace('<h1></h1>', f'<h1>Knowledge Graph - {len(all_nodes)} Nodes, {len(triples)} Relationships, {community_count} Communities</h1>')
    
    # Write back the modified HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Knowledge graph visualization saved to {output_file}")
    
    # Return statistics
    stats = {
        "nodes": len(all_nodes),
        "edges": len(triples),
        "communities": len(set(node_communities.values()))
    }
    print(f"Graph Statistics: {json.dumps(stats, indent=2)}")
    return stats

def sample_data_visualization():
    """Generate a visualization using sample data to test the functionality"""
    # Sample data representing knowledge graph triples
    sample_triples = [
        {"subject": "Industrial Revolution", "predicate": "began in", "object": "Great Britain"},
        {"subject": "Industrial Revolution", "predicate": "characterized by", "object": "machine manufacturing"},
        {"subject": "Industrial Revolution", "predicate": "led to", "object": "urbanization"},
        {"subject": "Industrial Revolution", "predicate": "led to", "object": "rise of capitalism"},
        {"subject": "Industrial Revolution", "predicate": "led to", "object": "new labor movements"},
        {"subject": "Industrial Revolution", "predicate": "fueled by", "object": "technological innovations"},
        {"subject": "James Watt", "predicate": "developed", "object": "steam engine"},
        {"subject": "James Watt", "predicate": "born in", "object": "Scottland"},
        {"subject": "Scottland", "predicate": "a country in", "object": "Europe"},
        {"subject": "steam engine", "predicate": "revolutionized", "object": "transportation"},
        {"subject": "steam engine", "predicate": "revolutionized", "object": "manufacturing processes"},
        {"subject": "steam engine", "predicate": "spread to", "object": "Europe"},
        {"subject": "steam engine", "predicate": "lead to", "object": "Industrial Revolution"},
        {"subject": "steam engine", "predicate": "spread to", "object": "North America"},
        {"subject": "technological innovations", "predicate": "led to", "object": "Digital Computers"},
        {"subject": "Digital Computers", "predicate": "enabled", "object": "Artificial Intelligence"},
        {"subject": "Artificial Intelligence", "predicate": "will replace", "object": "Humanity"},
        {"subject": "Artificial Intelligence", "predicate": "led to", "object": "LLMs"},
        {"subject": "Robert McDermott", "predicate": "likes", "object": "LLMs"},
        {"subject": "Robert McDermott", "predicate": "owns", "object": "Digital Computers"},
        {"subject": "Robert McDermott", "predicate": "lives in", "object": "North America"}
    ]
    
    # Generate the visualization
    output_file = "sample_knowledge_graph.html"
    print(f"Generating sample visualization with {len(sample_triples)} triples")
    stats = visualize_knowledge_graph(sample_triples, output_file)
    
    print("\nSample Knowledge Graph Statistics:")
    print(f"Nodes: {stats['nodes']}")
    print(f"Edges: {stats['edges']}")
    print(f"Communities: {stats['communities']}")
    
    print(f"\nVisualization saved to {output_file}")
    print(f"To view, open: file://{os.path.abspath(output_file)}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Knowledge Graph Generator and Visualizer')
    parser.add_argument('--test', action='store_true', help='Generate a test visualization with sample data')
    args = parser.parse_args()
    
    # If test flag is provided, generate a sample visualization
    if args.test:
        sample_data_visualization()
        return
    
    # Normal processing continues below
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration. Exiting.")
        return
    
    # Extract configuration values
    data = config["data"]["input"]
    
    # Choose which system prompt to use
    system_prompt = config["prompts"]["system_prompt"]
    user_prompt = config["prompts"]["user_prompt"]
    user_prompt += f"context: ```\n{data}```\n" 

    # LLM configuration
    model = config["llm"]["model"]
    api_key = config["llm"]["api_key"]
    max_tokens = config["llm"]["max_tokens"]
    temperature = config["llm"]["temperature"]
    
    # Process with LLM
    metadata = {}
    response = llm(model, user_prompt, api_key, system_prompt, max_tokens, temperature)
    
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
        
        # Visualize the knowledge graph
        output_file = "knowledge_graph.html"
        stats = visualize_knowledge_graph(result, output_file)
        print("\nKnowledge Graph Statistics:")
        print(f"Nodes: {stats['nodes']}")
        print(f"Edges: {stats['edges']}")
        print(f"Communities: {stats['communities']}")
        
        # Provide command to open the visualization in a browser
        print("\nTo view the visualization, open the following file in your browser:")
        print(f"file://{os.path.abspath(output_file)}")
    else:
        print("\n\nERROR ### Could not extract valid JSON from response: ", response, "\n\n")

def extract_json_from_text(text):
    """
    Extract JSON array from text that might contain additional content.
    Returns the parsed JSON if found, None otherwise.
    """
    # First, check if the text is wrapped in code blocks with triple backticks
    code_block_pattern = r'```(?:json)?\s*([\s\S]*?)```'
    code_match = re.search(code_block_pattern, text)
    if code_match:
        text = code_match.group(1).strip()
        print("Found JSON in code block, extracting content...")
    
    try:
        # Try direct parsing in case the response is already clean JSON
        return json.loads(text)
    except json.JSONDecodeError:
        # Look for opening and closing brackets of a JSON array
        start_idx = text.find('[')
        if start_idx == -1:
            print("No JSON array start found in text")
            return None
            
        # Simple bracket counting to find matching closing bracket
        bracket_count = 0
        complete_json = False
        for i in range(start_idx, len(text)):
            if text[i] == '[':
                bracket_count += 1
            elif text[i] == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    # Found the matching closing bracket
                    json_str = text[start_idx:i+1]
                    complete_json = True
                    break
        
        # Handle complete JSON array
        if complete_json:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                print("Found JSON-like structure but couldn't parse it.")
                print("Trying to fix common formatting issues...")
                
                # Try to fix missing quotes around keys
                fixed_json = re.sub(r'(\s*)(\w+)(\s*):(\s*)', r'\1"\2"\3:\4', json_str)
                # Fix trailing commas
                fixed_json = re.sub(r',(\s*[\]}])', r'\1', fixed_json)
                
                try:
                    return json.loads(fixed_json)
                except:
                    print("Could not fix JSON format issues")
        else:
            # Handle incomplete JSON - try to complete it
            print("Found incomplete JSON array, attempting to complete it...")
            
            # Get all complete objects from the array
            objects = []
            obj_start = -1
            obj_end = -1
            brace_count = 0
            
            # First find all complete objects
            for i in range(start_idx + 1, len(text)):
                if text[i] == '{':
                    if brace_count == 0:
                        obj_start = i
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        obj_end = i
                        objects.append(text[obj_start:obj_end+1])
            
            if objects:
                # Reconstruct a valid JSON array with complete objects
                reconstructed_json = "[\n" + ",\n".join(objects) + "\n]"
                try:
                    return json.loads(reconstructed_json)
                except json.JSONDecodeError:
                    print("Couldn't parse reconstructed JSON array.")
                    print("Trying to fix common formatting issues...")
                    
                    # Try to fix missing quotes around keys
                    fixed_json = re.sub(r'(\s*)(\w+)(\s*):(\s*)', r'\1"\2"\3:\4', reconstructed_json)
                    # Fix trailing commas
                    fixed_json = re.sub(r',(\s*[\]}])', r'\1', fixed_json)
                    
                    try:
                        return json.loads(fixed_json)
                    except:
                        print("Could not fix JSON format issues in reconstructed array")
            
        print("No complete JSON array could be extracted")
        return None

def llm(model, user_prompt, api_key, system_prompt=None, max_tokens=1000, temperature=0.2) -> str:
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {api_key}"
    }
    
    messages = []
    
    messages.append({
        'role': 'system',
        'content': system_prompt
        })
    
    messages.append({
        'role': 'user',
        'content': [
            {
                'type': 'text',
                'text': user_prompt
            }
        ]
    })
    
    payload = {
        'model': model,
        'messages': messages,
        'max_tokens': max_tokens,
        'temperature': temperature
    }
    
    response = requests.post(
        f"http://localhost:11434/v1/chat/completions",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise Exception(f"API request failed: {response.text}")


if __name__ == "__main__":
    main()
