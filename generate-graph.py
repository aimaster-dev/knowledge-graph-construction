#!/usr/bin/env python3
"""
Knowledge Graph Generator and Visualizer.
This script serves as a backward-compatible entry point to the refactored code.
"""
import sys
import os

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
    
from src.knowledge_graph.main import main

if __name__ == "__main__":
    # Pass command line arguments to the main function
    main()
