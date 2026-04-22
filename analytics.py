import json

with open("interop_property_graph.json", "r", encoding="utf-8") as f:
    data = json.load(f)

nodes = set()
edges = 0
agrovoc_links = 0
relations = {}

for item in data:
    nodes.add(item['subject'])
    nodes.add(item['object'])
    edges += 1
    if "AGROVOC" in str(item['object']):
        agrovoc_links += 1
    
    rel = item['relation']
    relations[rel] = relations.get(rel, 0) + 1

print(f"--- KRISHI GRAPH ANALYTICS ---")
print(f"Total Entities (Nodes): {len(nodes)}")
print(f"Total Relationships (Edges): {edges}")
print(f"Semantic Interoperability Rate: {(agrovoc_links/len(nodes))*100:.2f}%")
print(f"Graph Density: {edges / (len(nodes)*(len(nodes)-1)):.5f}")
print(f"\nRelationship Distribution:")
for r, count in relations.items():
    print(f"- {r}: {count}")