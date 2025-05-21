# Workflow Knowledge Graph Extractor

This project automates the extraction of workflow-related triples from unstructured text using the Gemini API and visualizes them as an interactive, editable knowledge graph. The resulting graph helps you discover, analyze, and automate workflows in your domain.



## Features

- **Automated Triple Extraction:**  
  Uses Gemini API to extract (subject, predicate, object) triples focused on workflow, process, and automation relationships from your text data.

- **Graph Construction:**  
  Builds a directed, connected knowledge graph using NetworkX, ensuring all concepts are linked.

- **Interactive Visualization:**  
  Visualizes the graph with PyVis, allowing you to:
  - Drag nodes to reposition them
  - Zoom and pan the view
  - Edit nodes and edges interactively in your browser

- **Workflow Discovery:**  
  Highlights workflow start/end points and process nodes for easy identification of automation opportunities.

---

## Requirements

- Python 3.8 or higher
- [Google Generative AI Python SDK](https://pypi.org/project/google-generativeai/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [networkx](https://pypi.org/project/networkx/)
- [pyvis](https://pypi.org/project/pyvis/)

---

## Installation

Install all dependencies using pip:

```bash
pip install google-generativeai python-dotenv networkx pyvis
```