import streamlit as st
import json
import base64
import streamlit.components.v1 as components
from pyvis.network import Network
from thefuzz import process

# 1. Page Configuration
st.set_page_config(page_title="KRISHI: Learning Knowledge Graph", layout="wide")

# 2. Load Data with Persistence
@st.cache_data
def load_data():
    try:
        with open("interop_property_graph.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

data = load_data()

# 3. Pre-compute Entity Index
@st.cache_data
def get_all_entities(_data):
    entities = set()
    for item in _data:
        if item.get("subject"): entities.add(item["subject"])
        if item.get("object"): entities.add(item["object"])
    return list(entities)

all_entities = get_all_entities(data)

# 4. Sidebar Legend
with st.sidebar:
    st.header("📊 Graph Legend")
    st.markdown("- 🟢 Crops | 🔴 Diseases | 🟠 Pests\n- 🔵 Inputs | ⚪ AGROVOC | 🔘 Other")
    st.divider()
    st.info("💡 **Learning Mode:** Clicking '✅ Correct' ranks that result higher for future searches.")

# 5. UI: KRISHI Semantic Search
st.title("🌾 KRISHIKG")

query = st.text_input("Ask a question (e.g., 'നെല്ലിനെ ബാധിക്കുന്ന രോഗങ്ങൾ'):")

if query and all_entities:
    query_tokens = query.split()
    found_entities = []
    
    # Advanced Stemming & Fuzzy Logic
    for token in query_tokens:
        # Substring check for Malayalam suffixes
        for entity in all_entities:
            if entity in token or token in entity:
                found_entities.append(entity)
        # Fuzzy backup
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
        related = sorted(related, key=lambda x: x.get('weight', 0), reverse=True)

        if related:
            st.subheader("Top Results")
            for i, t in enumerate(related[:10]): # Limit to top 10 for clean UI
                with st.container():
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        weight = t.get('weight', 0)
                        stars = "⭐" * min(weight, 5) if weight > 0 else ""
                        st.write(f"**{t['subject']}** → *{t['relation']}* → **{t['object']}** {stars}")
                        if t.get('context'): st.caption(f"Context: {t['context']}")
                    
                    with c2:
                        if st.button("✅", key=f"v_{i}_{t['subject']}"):
                            t['weight'] = t.get('weight', 0) + 1
                            with open("interop_property_graph.json", "w", encoding="utf-8") as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                            st.rerun()
                st.divider()
        else:
            st.info("No relationships found for these terms.")

# 6. Graph Visualization Engine
st.subheader("Interactive Knowledge Map")
net = Network(height="600px", width="100%", bgcolor="#0E1117", font_color="white", notebook=False)
net.force_atlas_2based(gravity=-50, spring_length=100)

COLORS = {"CROP": "#2ed573", "DISEASE": "#ff4757", "PEST": "#ffa502", "INPUT": "#1e90ff", "ANCHOR": "#ffffff", "DEFAULT": "#ced6e0"}

# Displaying first 150 edges to keep the browser fast
for item in data[:150]:
    subj, obj, rel = item.get("subject"), item.get("object"), item.get("relation")
    if subj and obj:
        s_col = COLORS["ANCHOR"] if "AGROVOC" in str(subj) else COLORS.get(item.get("subject_type", "DEFAULT"), COLORS["DEFAULT"])
        o_col = COLORS["ANCHOR"] if "AGROVOC" in str(obj) else COLORS.get(item.get("object_type", "DEFAULT"), COLORS["DEFAULT"])
        
        net.add_node(subj, label=subj, color=s_col, size=30 if "AGROVOC" in str(subj) else 20)
        net.add_node(obj, label=obj, color=o_col, size=30 if "AGROVOC" in str(obj) else 20)
        net.add_edge(subj, obj, title=rel, label=rel, color="#555555")

html_string = net.generate_html()
b64_html = base64.b64encode(html_string.encode('utf-8')).decode()
components.html(f'<iframe src="data:text/html;base64,{b64_html}" width="100%" height="650px" style="border:none;"></iframe>', height=650)