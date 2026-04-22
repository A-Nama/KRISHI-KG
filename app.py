import streamlit as st
import json
import base64
import streamlit.components.v1 as components
from pyvis.network import Network
from thefuzz import process
import os

# 1. Page Configuration
st.set_page_config(page_title="KRISHI KG", layout="wide")

# Ensure pyvis has a writable temporary directory for cloud environments
os.environ['MPLCONFIGDIR'] = os.getcwd() + "/.config/"

# 2. Load Data with Persistence
@st.cache_data
def load_data():
    try:
        with open("interop_property_graph.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Data file 'interop_property_graph.json' not found.")
        return []

data = load_data()

# 3. Pre-compute Entity Index
@st.cache_data
def get_all_entities(_data):
    entities = set()
    for item in _data:
        if item.get("subject"): entities.add(str(item["subject"]))
        if item.get("object"): entities.add(str(item["object"]))
    return list(entities)

all_entities = get_all_entities(data)

# 4. Sidebar Legend with New Line Formatting
with st.sidebar:
    st.header("📊 Graph Legend")
    st.markdown("""
- 🟢 **Crops**
- 🔴 **Diseases**
- 🟠 **Pests**
- 🔵 **Inputs**
- ⚪ **AGROVOC Anchors**
- 🔘 **Other**
    """)
    st.divider()
    st.info("💡 **Learning Mode:** Clicking '✅' ranks that result higher. Results are sorted by relevance.")

# 5. UI: KRISHI Semantic Search
st.title("🌾 KRISHI KG")

query = st.text_input("Ask a question (e.g., 'നെല്ലിനെ ബാധിക്കുന്ന രോഗങ്ങൾ'):")

if query and all_entities:
    query_tokens = query.split()
    found_entities = []
    
    # Advanced Stemming & Fuzzy Logic
    for token in query_tokens:
        # 1. Substring check for Malayalam suffixes (e.g., Nelline -> Nellu)
        for entity in all_entities:
            if entity in token or token in entity:
                found_entities.append(entity)
        
        # 2. Fuzzy backup for typos
        match_result = process.extractOne(token, all_entities, score_cutoff=70)
        if match_result:
            found_entities.append(match_result[0])
    
    found_entities = list(set(found_entities))

    if found_entities:
        # Toggle to hide/show identified entities
        with st.expander("🛠️ View Identified Entities", expanded=False):
            st.write(f"Matched Tokens: {', '.join([f'`{e}`' for e in found_entities])}")

        # Filter & Rank Triples by Weight
        related = [t for t in data if t.get('subject') in found_entities or t.get('object') in found_entities]
        # Sort by weight (highest first)
        related = sorted(related, key=lambda x: x.get('weight', 0), reverse=True)

        if related:
            st.subheader("Top Results")
            for i, t in enumerate(related[:15]): # Show top 15 results
                with st.container():
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        weight = t.get('weight', 0)
                        stars = "⭐" * min(weight, 5) if weight > 0 else ""
                        st.write(f"**{t['subject']}** → *{t['relation']}* → **{t['object']}** {stars}")
                        if t.get('context'): st.caption(f"Context: {t['context']}")
                    
                    with c2:
                        # Feedback button updates JSON weight
                        if st.button("✅", key=f"v_{i}_{t['subject']}"):
                            t['weight'] = t.get('weight', 0) + 1
                            with open("interop_property_graph.json", "w", encoding="utf-8") as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                            st.rerun()
                st.divider()
        else:
            st.info("No direct relationships found for these terms.")

# 6. Graph Visualization Engine
st.subheader("Interactive Knowledge Map")
net = Network(height="650px", width="100%", bgcolor="#0E1117", font_color="white", notebook=False)
net.force_atlas_2based(gravity=-50, central_gravity=0.01, spring_length=100, damping=0.4)

COLORS = {
    "CROP": "#2ed573", "DISEASE": "#ff4757", "PEST": "#ffa502", 
    "INPUT": "#1e90ff", "ANCHOR": "#ffffff", "DEFAULT": "#ced6e0"
}

# Display full graph (or first 250 nodes for speed)
for item in data[:250]:
    subj, obj, rel = item.get("subject"), item.get("object"), item.get("relation")
    if subj and obj:
        s_str, o_str = str(subj), str(obj)
        
        # Enhanced Anchor Detection (Case-Insensitive)
        is_s_anchor = "AGROVOC" in s_str.upper()
        is_o_anchor = "AGROVOC" in o_str.upper()

        # Styling
        s_col = COLORS["ANCHOR"] if is_s_anchor else COLORS.get(item.get("subject_type", "DEFAULT"), COLORS["DEFAULT"])
        s_size = 40 if is_s_anchor else 25
        
        o_col = COLORS["ANCHOR"] if is_o_anchor else COLORS.get(item.get("object_type", "DEFAULT"), COLORS["DEFAULT"])
        o_size = 40 if is_o_anchor else 25
        
        net.add_node(s_str, label=s_str, color=s_col, size=s_size, font={'color': 'white'})
        net.add_node(o_str, label=o_str, color=o_col, size=o_size, font={'color': 'white'})
        
        # Tooltip
        ctx = item.get("context", "")
        tooltip = f"<b>Rel:</b> {rel}<br><b>Ctx:</b> {ctx}" if ctx else rel
        net.add_edge(s_str, o_str, title=tooltip, label=rel, color="#888888", font={'size': 10})

# Render via Base64 to handle Cloud Iframe restrictions
html_string = net.generate_html()
b64_html = base64.b64encode(html_string.encode('utf-8')).decode()
components.html(
    f'<iframe src="data:text/html;base64,{b64_html}" width="100%" height="700px" style="border:none; background-color: #0E1117;"></iframe>',
    height=700,
)