import json
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# 1. Load the data
with open("interop_property_graph.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. Extract Data for Distribution
relations = [item['relation'] for item in data]
nodes = []
for item in data:
    nodes.append(item['subject'])
    nodes.append(item['object'])

rel_counts = Counter(relations).most_common()
node_counts = Counter(nodes).most_common(10) # Top 10 Hubs

# Set the aesthetic style
sns.set_theme(style="whitegrid")

# --- PLOT 1: Relationship Distribution ---
plt.figure(figsize=(10, 6))
rel_df = { "Relation": [r[0] for r in rel_counts], "Count": [r[1] for r in rel_counts] }
ax = sns.barplot(x="Count", y="Relation", data=rel_df, palette="viridis")
plt.title("Distribution of Semantic Relationships in KRISHI Graph", fontsize=15)
plt.xlabel("Frequency", fontsize=12)
plt.ylabel("Relationship Type (Predicates)", fontsize=12)

# Add values on bars
for i in ax.containers:
    ax.bar_label(i,)

plt.tight_layout()
plt.savefig("relation_distribution.png")
plt.show()

# --- PLOT 2: Top Knowledge Hubs (Most Connected Entities) ---
plt.figure(figsize=(10, 6))
node_df = { "Entity": [n[0] for n in node_counts], "Degree": [n[1] for n in node_counts] }
ax2 = sns.barplot(x="Degree", y="Entity", data=node_df, palette="magma")
plt.title("Top 10 Knowledge Hubs (Entity Degree Centrality)", fontsize=15)
plt.xlabel("Number of Connections (Degree)", fontsize=12)
plt.ylabel("Entity Name", fontsize=12)

plt.tight_layout()
plt.savefig("top_hubs.png")
plt.show()