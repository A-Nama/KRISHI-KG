import json
import requests
from pyvis.network import Network

print("Igniting Knowledge Graph Builder...")

# 1. Load the data LangExtract just pulled
with open("multi_lingual_nodes.json", "r", encoding="utf-8") as f:
    nodes = json.load(f)

# 2. The Local Dictionary (Fills the gap for Dravidian languages in AGROVOC)
malayalam_map = {
    "നെല്ല്": "Rice",
    "വേപ്പെണ്ണ": "Neem oil",
    "ഫംഗസ്": "Fungus",
    "യൂറിയ": "Urea",
    "കുരുമുളക്": "Black pepper",
    "കാരറ്റ്": "Carrot",
    "ചാണകപ്പൊടി": "Cow dung",
    "വേപ്പിൻപിണ്ണാക്ക്": "Neem cake",
    "എല്ലുപൊടി": "Bone meal",
    "ജൈവവളങ്ങൾ": "Organic fertilizer"
}

def get_agrovoc_id(term, lang_code):
    search_term = malayalam_map.get(term, term)
    api_lang = "en" if term in malayalam_map else lang_code

    try:
        # Ping the real UN database
        url = f"https://agrovoc.fao.org/browse/rest/v1/search/?query={search_term}&lang={api_lang}"
        response = requests.get(url, timeout=5).json()
        
        if response.get('results'):
            uri = response['results'][0]['uri']
            concept_id = uri.split("/")[-1] 
            return f"{search_term}\n({concept_id})"
    except Exception:
        pass 
    
    return f"{search_term}\n(Unmapped)"

# 3. Setup the PyVis Canvas 
net = Network(height="800px", width="100%", bgcolor="#0d1117", font_color="white", select_menu=True)
net.force_atlas_2based(gravity=-50) 

for item in nodes:
    local_word = item["text"]
    entity_type = item["class"]
    
    # Language Detection logic to color-code the bubbles
    if any("\u0D00" <= c <= "\u0D7F" for c in local_word):
        lang, color = "ml", "#00a8ff" # Blue for Malayalam
    elif any("\u4e00" <= c <= "\u9fff" for c in local_word):
        lang, color = "zh", "#ff4757" # Red for Chinese
    else:
        lang, color = "en", "#ffa502" # Orange for English

    print(f"Mapping {lang.upper()} term: {local_word}...")
    
    universal_node = get_agrovoc_id(local_word, lang)
    
    # Add nodes and edges to the graph
    net.add_node(universal_node, label=universal_node, color="#2ed573", size=40, shape="hexagon")
    net.add_node(local_word, label=local_word, color=color, size=20, title=f"Dataset Lang: {lang}")
    net.add_edge(local_word, universal_node, title=f"Type: {entity_type}", color="#ffffff")

# 4. Render the final HTML
html = net.generate_html()
with open("final_research_graph.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Done! Open 'final_research_graph.html' to view your interoperable graph.")