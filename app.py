import streamlit as st
import json
import base64
import streamlit.components.v1 as components
from pyvis.network import Network

# 1. Page Configuration
st.set_page_config(page_title="KRISHI Knowledge Graph", layout="wide")

st.title("KRISHI: Interactive Property Graph")
st.markdown("""
Explore agricultural relationships extracted natively from Malayalam datasets. 
**Hover over edges** to see contextual metadata (dosages, conditions). 
**Use the sidebar** to filter or understand the color coding.
""")

# 2. Sidebar Legend & Info
with st.sidebar:
    st.header("Graph Legend")
    st.markdown("""
    - 🟢 **Green**: Crops
    - 🔴 **Red**: Diseases
    - 🟠 **Orange**: Pests
    - 🔵 **Blue**: Inputs (Fertilizers/Water)
    - ⚪ **White (Large)**: AGROVOC Anchors
    - 🔘 **Grey**: Other/Locations
    """)
    st.divider()
    st.info("💡 **Tip:** You can drag nodes to rearrange the graph or use the scroll wheel to zoom.")

# 3. Load the Data
@st.cache_data
def load_data():
    # Ensure this filename matches your interoperable JSON file
    with open("interop_property_graph.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# 4. Color Palette Mapping
COLORS = {
    "CROP": "#2ed573",      # Fresh Green
    "DISEASE": "#ff4757",   # Alert Red
    "PEST": "#ffa502",      # Warning Orange
    "INPUT": "#1e90ff",     # Blue
    "LOC": "#70a1ff",       # Sky Blue
    "ANCHOR": "#ffffff",    # White for AGROVOC
    "DEFAULT": "#ced6e0"    # Grey
}

# 5. Build Graph
# We disable notebook=False as we are generating a standalone HTML string
net = Network(height="700px", width="100%", bgcolor="#0E1117", font_color="white", notebook=False)

# Professional Physics Settings
net.force_atlas_2based(gravity=-50, central_gravity=0.01, spring_length=100, damping=0.4)

for item in data:
    subj = item.get("subject")
    obj = item.get("object")
    rel = item.get("relation")
    ctx = item.get("context", "")
    
    # Get types for specific coloring
    s_type = item.get("subject_type", "DEFAULT")
    o_type = item.get("object_type", "DEFAULT")

    if subj and obj:
        # Determine Subject Style
        if "AGROVOC" in str(subj):
            s_color, s_size = COLORS["ANCHOR"], 35
        else:
            s_color = COLORS.get(s_type, COLORS["DEFAULT"])
            s_size = 25

        # Determine Object Style
        if "AGROVOC" in str(obj):
            o_color, o_size = COLORS["ANCHOR"], 35
        else:
            o_color = COLORS.get(o_type, COLORS["DEFAULT"])
            o_size = 25

        # Add Nodes
        net.add_node(subj, label=subj, color=s_color, size=s_size, title=f"Type: {s_type}")
        net.add_node(obj, label=obj, color=o_color, size=o_size, title=f"Type: {o_type}")
        
        # Add Edge
        # The 'title' attribute creates the hover tooltip
        tooltip = f"<b>Relationship:</b> {rel}<br><b>Context:</b> {ctx}" if ctx else rel
        net.add_edge(subj, obj, title=tooltip, label=rel, color="#888888", font={'size': 10, 'align': 'middle'})

# 6. Generate and Display
# We use the Base64 encoding method to ensure the iframe loads correctly
html_string = net.generate_html()
b64_html = base64.b64encode(html_string.encode('utf-8')).decode()

components.html(
    f'<iframe src="data:text/html;base64,{b64_html}" width="100%" height="750px" style="border:none; background-color: #0E1117;"></iframe>',
    height=800,
)