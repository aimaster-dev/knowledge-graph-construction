"""Visualization utilities for knowledge graphs."""
import networkx as nx
import json
import re
import os
from pyvis.network import Network

# HTML template for visualization is now stored in a separate file
def _load_html_template():
    """Load the HTML template from the template file."""
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'graph_template.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not load template file: {e}")
        return '<div id="mynetwork" class="card-body"></div>'  # Fallback to basic template

def visualize_knowledge_graph(triples, output_file="knowledge_graph.html"):
    """
    Create and visualize a knowledge graph from subject-predicate-object triples.
    
    Args:
        triples: List of dictionaries with 'subject', 'predicate', and 'object' keys
        output_file: HTML file to save the visualization
        
    Returns:
        Dictionary with graph statistics
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
    
    # Calculate centrality metrics
    centrality_metrics = _calculate_centrality_metrics(G_undirected, all_nodes)
    betweenness = centrality_metrics["betweenness"]
    degree = centrality_metrics["degree"]
    eigenvector = centrality_metrics["eigenvector"]
    
    # Calculate communities
    node_communities, community_count = _detect_communities(G_undirected, all_nodes)
    
    # Define colors for communities - these are standard colorblind-friendly colors
    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33', '#a65628', '#f781bf']
    
    # Calculate node sizes based on centrality metrics
    node_sizes = _calculate_node_sizes(all_nodes, betweenness, degree, eigenvector)
    
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
    _add_nodes_and_edges_to_network(net, G)
    
    # Set visualization options
    options = _get_visualization_options()
    
    # Set all options in one go with proper JSON
    net.set_options(json.dumps(options))
    
    # Save the network as HTML and modify with custom template
    _save_and_modify_html(net, output_file, community_count, all_nodes, triples)
    
    # Return statistics
    stats = {
        "nodes": len(all_nodes),
        "edges": len(triples),
        "communities": len(set(node_communities.values()))
    }
    print(f"Graph Statistics: {json.dumps(stats, indent=2)}")
    return stats

def _calculate_centrality_metrics(G_undirected, all_nodes):
    """Calculate centrality metrics for the graph nodes."""
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
    
    return {
        "betweenness": betweenness,
        "degree": degree,
        "eigenvector": eigenvector
    }

def _detect_communities(G_undirected, all_nodes):
    """Detect communities in the graph."""
    try:
        # Attempt to detect communities using Louvain method
        import community as community_louvain
        partition = community_louvain.best_partition(G_undirected)
        community_count = len(set(partition.values()))
        print(f"Detected {community_count} communities using Louvain method")
        return partition, community_count
    except:
        # Fallback: assign community IDs based on degree for simplicity
        node_communities = {}
        for node in all_nodes:
            node_degree = G_undirected.degree(node) if node in G_undirected else 0
            # Ensure we have at least 0 as a community ID
            community_id = max(0, node_degree) % 8  # Using modulo 8 to limit number of colors
            node_communities[node] = community_id
        community_count = len(set(node_communities.values()))
        print(f"Using degree-based communities ({community_count} communities)")
        return node_communities, community_count

def _calculate_node_sizes(all_nodes, betweenness, degree, eigenvector):
    """Calculate node sizes based on centrality metrics."""
    # Find max values for normalization
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
    
    return node_sizes

def _add_nodes_and_edges_to_network(net, G):
    """Add nodes and edges from NetworkX graph to PyVis network."""
    # Add nodes with all their attributes
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
    
    # Add edges with all their attributes
    for edge in G.edges(data=True):
        source, target, data = edge
        net.add_edge(
            source, 
            target, 
            title=data.get('title', ''),
            label=data.get('label', ''),
            arrows="to"
        )

def _get_visualization_options():
    """Get options for PyVis visualization."""
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
    
    # Full options for visualization
    return {
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

def _save_and_modify_html(net, output_file, community_count, all_nodes, triples):
    """Save the network as HTML and modify with custom template."""
    # Save the network as HTML
    net.save_graph(output_file)
    
    # Read the generated HTML
    with open(output_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Add our custom controls by replacing the div with our template
    html = html.replace('<div id="mynetwork" class="card-body"></div>', _load_html_template())
    
    # Fix the duplicate title issue
    # Remove the default PyVis header
    html = re.sub(r'<center>\s*<h1>.*?</h1>\s*</center>', '', html)
    
    # Replace the other h1 with our enhanced title
    html = html.replace('<h1></h1>', f'<h1>Knowledge Graph - {len(all_nodes)} Nodes, {len(triples)} Relationships, {community_count} Communities</h1>')
    
    # Write back the modified HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Knowledge graph visualization saved to {output_file}")

def sample_data_visualization(output_file="sample_knowledge_graph.html"):
    """
    Generate a visualization using sample data to test the functionality.
    
    Args:
        output_file: Path to save the sample graph HTML
    """
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
    print(f"Generating sample visualization with {len(sample_triples)} triples")
    stats = visualize_knowledge_graph(sample_triples, output_file)
    
    print("\nSample Knowledge Graph Statistics:")
    print(f"Nodes: {stats['nodes']}")
    print(f"Edges: {stats['edges']}")
    print(f"Communities: {stats['communities']}")
    
    print(f"\nVisualization saved to {output_file}")
    print(f"To view, open: file://{os.path.abspath(output_file)}") 

if __name__ == "__main__":
    # Run sample visualization when this module is run directly
    sample_data_visualization() 