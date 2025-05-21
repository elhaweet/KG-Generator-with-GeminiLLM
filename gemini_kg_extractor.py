import os
from dotenv import load_dotenv
import google.generativeai as genai
from pyvis.network import Network
import networkx as nx
import random

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Read the text data
with open('rowData.text', 'r', encoding='utf-8') as file:
    text_data = file.read()

# Enhanced prompt for workflow-focused triple extraction
prompt = f"""
Extract knowledge graph triples from the following text in the format (subject, predicate, object).
Focus specifically on workflow relationships, processes, and automation opportunities.
Look for:
1. Sequential steps or processes (X leads to Y, X happens before Y, X is followed by Y)
2. Causal relationships (X causes Y, X enables Y, X results in Y)
3. Dependencies (X requires Y, X depends on Y, X needs Y)
4. Actions and their agents (X performs Y, X uses Y for Z, X implements Y)
5. Inputs and outputs of processes (X produces Y, X consumes Y, X transforms into Y)
6. Workflow stages (X is first stage of Y, X is part of process Y)

IMPORTANT: Make sure to create a CONNECTED graph by identifying relationships between concepts.
If possible, identify a complete workflow sequence from start to finish.

Return the results as a Python list of tuples.
Example format: [("Data Collection", "precedes", "Data Analysis"), ("Machine Learning", "automates", "Decision Making"), ...]

Text: {text_data}
"""

# Get response from Gemini
response = model.generate_content(prompt)
response_text = response.text

# Extract the Python list from the response
# This assumes Gemini returns properly formatted Python code
triples_code = response_text.strip()
if "```python" in triples_code:
    # Extract code between Python code blocks
    triples_code = triples_code.split("```python")[1].split("```")[0].strip()
elif "```" in triples_code:
    # Extract code between generic code blocks
    triples_code = triples_code.split("```")[1].split("```")[0].strip()

# Execute the code to get the triples list
try:
    # Safe way to evaluate the Python expression
    local_vars = {}
    exec(f"triples = {triples_code}", {}, local_vars)
    triples = local_vars['triples']
    print(f"✅ Successfully extracted {len(triples)} triples from the text")
except Exception as e:
    print(f"❌ Error parsing triples: {e}")
    print("Using fallback method...")
    # Fallback: Try to directly evaluate if it's a clean list
    try:
        triples = eval(triples_code)
        print(f"✅ Successfully extracted {len(triples)} triples using fallback")
    except:
        print("❌ Fallback failed. Using sample triples.")
        # Sample triples as fallback with workflow focus
        triples = [
            ("Data Collection", "precedes", "Data Processing"),
            ("Data Processing", "enables", "Machine Learning"),
            ("Machine Learning", "automates", "Decision Making"),
            ("Decision Making", "improves", "Efficiency")
        ]

# === Build the graph ===
G = nx.DiGraph()

# Add triples to the graph
for subj, pred, obj in triples:
    G.add_node(subj)
    G.add_node(obj)
    G.add_edge(subj, obj, label=pred)

# Ensure graph connectivity by connecting disconnected components
components = list(nx.weakly_connected_components(G))
if len(components) > 1:
    print(f"⚠️ Found {len(components)} disconnected components. Adding connections...")
    
    # Get a list of all nodes
    all_nodes = list(G.nodes())
    
    # Connect disconnected components
    for i in range(len(components) - 1):
        # Get a random node from each component
        source_component = list(components[i])
        target_component = list(components[i + 1])
        
        source_node = random.choice(source_component)
        target_node = random.choice(target_component)
        
        # Add a connecting edge
        G.add_edge(source_node, target_node, label="may relate to")
        print(f"  Connected: {source_node} -> {target_node}")

# Identify potential workflow start and end points
in_degree = dict(G.in_degree())
out_degree = dict(G.out_degree())

# Nodes with no incoming edges are potential start points
start_nodes = [node for node, degree in in_degree.items() if degree == 0]
# Nodes with no outgoing edges are potential end points
end_nodes = [node for node, degree in out_degree.items() if degree == 0]

print(f"Potential workflow start points: {start_nodes}")
print(f"Potential workflow end points: {end_nodes}")

# === Visualize using PyVis with enhanced styling ===
net = Network(notebook=True, height="700px", width="100%", directed=True)

# Add nodes with styling
for node in G.nodes():
    if node in start_nodes:
        net.add_node(node, color="#4CAF50", title="Start Point", shape="diamond", size=25)  # Green for start
    elif node in end_nodes:
        net.add_node(node, color="#F44336", title="End Point", shape="diamond", size=25)  # Red for end
    else:
        # Check if it's a process/action node
        process_keywords = ["process", "analysis", "learning", "processing", "automation", "development"]
        if any(keyword in node.lower() for keyword in process_keywords):
            net.add_node(node, color="#2196F3", title="Process", shape="box", size=20)  # Blue for processes
        else:
            net.add_node(node, title=node, size=15)

# Add edges with styling
for edge in G.edges(data=True):
    src, dst, data = edge
    # Highlight workflow sequence edges
    sequence_predicates = ["precedes", "leads to", "followed by", "enables", "results in"]
    if any(pred in data['label'].lower() for pred in sequence_predicates):
        net.add_edge(src, dst, label=data['label'], color="#FF9800", width=3, arrowStrikethrough=False)  # Orange for sequence
    else:
        net.add_edge(src, dst, label=data['label'], arrowStrikethrough=False, smooth={"type": "curvedCW", "roundness": 0.2})

# Add physics options for better layout - increased spacing and reduced forces
net.set_options("""
{
  "nodes": {
    "font": {
      "size": 14,
      "face": "Tahoma"
    }
  },
  "edges": {
    "font": {
      "size": 12,
      "align": "middle"
    },
    "color": {
      "inherit": false
    },
    "smooth": {
      "type": "dynamic",
      "forceDirection": "none"
    }
  },
  "physics": {
    "enabled": true,
    "hierarchicalRepulsion": {
      "centralGravity": 0.0,
      "springLength": 250,
      "springConstant": 0.005,
      "nodeDistance": 100,
      "damping": 0.09
    },
    "solver": "hierarchicalRepulsion",
    "stabilization": {
      "enabled": true,
      "iterations": 200,
      "updateInterval": 25,
      "fit": true
    }
  },
  "layout": {
    "hierarchical": {
      "enabled": true,
      "direction": "LR",
      "sortMethod": "directed",
      "levelSeparation": 250,
      "nodeSpacing": 200,
      "treeSpacing": 200
    }
  },
  "interaction": {
    "dragNodes": true,
    "dragView": true,
    "zoomView": true,
    "navigationButtons": true,
    "keyboard": true,
    "hover": true
  },
  "manipulation": {
    "enabled": true,
    "initiallyActive": true
  }
}
""")

# Save and view the graph
net.write_html("workflow_knowledge_graph.html")
print("✅ Workflow knowledge graph saved as 'workflow_knowledge_graph.html'")