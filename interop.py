import json
import requests
import time
import os
from googletrans import Translator

# 1. Setup Translator
translator = Translator()

# 2. AGROVOC API Helper
def get_agrovoc_id(english_term):
    try:
        # We use a broader search and clean the term for better AGROVOC matching
        clean_term = english_term.strip().lower()
        url = f"https://agrovoc.fao.org/browse/rest/v1/search/?query={clean_term}&lang=en"
        response = requests.get(url, timeout=10).json()
        if response.get('results'):
            # Extract ID (e.g., 'c_1234') from the URI
            return response['results'][0]['uri'].split('/')[-1]
    except Exception as e:
        print(f"AGROVOC Error for {english_term}: {e}")
        return None

# 3. Process Data
# Make sure this filename matches your current JSON
input_file = "krishiNERFinal.json"
output_file = "interop_property_graph.json"

if not os.path.exists(input_file):
    print(f"Error: {input_file} not found!")
    exit()

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract Unique Entities to minimize API calls
unique_terms = set()
for item in data:
    # Only map specific categories to AGROVOC to save time/quota
    if item.get("subject_type") in ["CROP", "INPUT", "DISEASE", "PEST"]:
        unique_terms.add(item["subject"])
    if item.get("object_type") in ["CROP", "INPUT", "DISEASE", "PEST"]:
        unique_terms.add(item["object"])

anchor_triples = []
print(f"Mapping {len(unique_terms)} unique terms to AGROVOC via GoogleTrans...")

for i, term in enumerate(unique_terms):
    try:
        # Step A: Translate ML -> EN
        # src='ml' (Malayalam), dest='en' (English)
        translation = translator.translate(term, src='ml', dest='en')
        en_term = translation.text
        
        # Step B: Get AGROVOC ID
        ag_id = get_agrovoc_id(en_term)
        
        if ag_id:
            anchor_triples.append({
                "subject": term,
                "subject_type": "LOCAL_TERM",
                "relation": "SAME_AS",
                "object": f"AGROVOC:{ag_id}",
                "object_type": "UNIVERSAL_ANCHOR",
                "context": f"Universal Anchor for {en_term}"
            })
            print(f"[{i+1}/{len(unique_terms)}] Linked: {term} -> {en_term} ({ag_id})")
        else:
            print(f"[{i+1}/{len(unique_terms)}] No AGROVOC match for: {term} ({en_term})")
        
        # Tiny sleep to prevent being flagged as a bot by Google Translate
        time.sleep(0.5) 

    except Exception as e:
        print(f"Error processing '{term}': {e}")
        # If blocked, increase sleep time
        time.sleep(2)

# 4. Save the expanded graph
with open(output_file, "w", encoding="utf-8") as f:
    # Combine original triples with the new interoperability anchors
    json.dump(data + anchor_triples, f, indent=2, ensure_ascii=False)

print(f"\n✨ Masterpiece complete! Saved to {output_file}")
print(f"🔗 Added {len(anchor_triples)} universal anchor nodes.")