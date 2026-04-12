import json
from pyvis.network import Network

def generate_static_graph():
    # 1. Load Data
    with open("krishiNERFinal.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. Initialize Network
    # notebook=False is essential for standalone HTML files
    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white")
    net.force_atlas_2based()

    # 3. Add Data
    for item in data:
        subj, obj, rel = item.get("subject"), item.get("object"), item.get("relation")
        ctx = item.get("context", "")
        
        if subj and obj:
            net.add_node(subj, label=subj, color="#00a8ff")
            net.add_node(obj, label=obj, color="#2ed573")
            tooltip = f"Context: {ctx}" if ctx else rel
            net.add_edge(subj, obj, title=tooltip, label=rel)

    # 4. Save with explicit UTF-8 encoding
    # We use generate_html to catch the string and write it manually to be safe
    html_content = net.generate_html()
    with open("graph_documentation.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("Success: graph_documentation.html generated.")

if __name__ == "__main__":
    generate_static_graph()