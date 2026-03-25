import langextract as lx
import os
import json
import random
import time

# Plug in your free Google AI Studio API key here
os.environ["LANGEXTRACT_API_KEY"] = "apikeyhere"

print("Booting Multi-Source Extractor...")

# --- SMART DATA LOADERS ---

def load_examples_from_label_studio(filepath):
    """Reads your manually annotated sentences directly from Label Studio"""
    print(f"Loading Few-Shot Examples from {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    examples = []
    for item in data:
        text = item.get('text', item.get('Content', ''))
        extractions = []
        for label_data in item.get('label', []):
            extracted_text = label_data.get('text')
            extraction_class = label_data.get('labels', [''])[0] 
            extractions.append(lx.data.Extraction(extraction_class=extraction_class, extraction_text=extracted_text))
        examples.append(lx.data.ExampleData(text=text, extractions=extractions))
    return examples

def load_agrichn_bio(filepath, sample_size=5):
    """Stitches Chinese characters from BIO format back into normal sentences"""
    print(f"Loading Chinese sentences from {filepath}...")
    sentences, current_sentence = [], ""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: 
                if current_sentence:
                    sentences.append(current_sentence)
                    current_sentence = ""
            else:
                current_sentence += line.split()[0]
    if current_sentence: sentences.append(current_sentence)
    return random.sample(sentences, min(sample_size, len(sentences)))

def load_agriner_json(filepath, sample_size=5):
    """Extracts raw English sentences from the AgriNER test_data.json"""
    print(f"Loading English sentences from {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # We just grab the 'text' string from each JSON object and ignore their pre-made entities
        sentences = [item.get("text", "") for item in data if "text" in item]
        return random.sample(sentences, min(sample_size, len(sentences)))
    except Exception as e:
        print(f"Error loading AgriNER: {e}")
        return []

def load_raw_txt(filepath, sample_size=5):
    """Loads standard Malayalam sentences"""
    print(f"Loading Malayalam sentences from {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    return random.sample(lines, min(sample_size, len(lines)))


# --- EXECUTE THE PIPELINE ---

# 1. Load your 5 perfect examples
examples = load_examples_from_label_studio("krishi_5_annotated.json")

# 2. Load the raw datasets
ml_sentences = load_raw_txt("krishi_ner_clean.txt", sample_size=10) 
zh_sentences = load_agrichn_bio("test.txt", sample_size=5)
en_sentences = load_agriner_json("test_data.json", sample_size=5) 

all_sentences = ml_sentences + zh_sentences + en_sentences

# 3. The Extraction Engine
prompt = "Extract agricultural entities (CROP, DISEASE, INPUT, PEST) from the text. Use exact text from the source."
all_results = []
extracted_nodes = []

print(f"Processing {len(all_sentences)} multi-lingual sentences through LangExtract...")

for text in all_sentences:
    try:
        result = lx.extract(
            text_or_documents=text,
            prompt_description=prompt,
            examples=examples,
            model_id="gemini-2.5-flash" 
        )
        all_results.append(result)
        
        for ext in result.extractions:
            extracted_nodes.append({
                "class": ext.extraction_class,
                "text": ext.extraction_text
            })
            
        print("Success! Sleeping for 13 seconds to respect API rate limits...")
        time.sleep(13) # This completely prevents the 429 Quota Error
        
    except Exception as e:
        print(f"Skipping a sentence due to API error: {e}")
        time.sleep(13) # Sleep even on an error to reset the timer

# --- SAVE OUTPUTS ---
print("Generating final files...")

# Fix: Visualize only the first successful document for your demo
if len(all_results) > 0:
    html_content = lx.visualize(all_results[0]) 
    with open("dataset_highlights.html", "w", encoding="utf-8") as f:
        f.write(html_content)

with open("multi_lingual_nodes.json", "w", encoding="utf-8") as f:
    json.dump(extracted_nodes, f, ensure_ascii=False, indent=2)

print("Success! 'dataset_highlights.html' and 'multi_lingual_nodes.json' are ready.")