import google.generativeai as genai
import os
import json
import time

# 1. Setup API
os.environ["GOOGLE_API_KEY"] = "apikey"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

print("Starting the KRISHI Relation Extraction Engine...")

# 2. Load raw dataset
with open("krishi_ner_clean.txt", "r", encoding="utf-8") as f:
    # This reads every line, removes extra spaces, and ignores blank lines
    all_sentences = [line.strip() for line in f if line.strip()]


# 3. The "Few-Shot" Prompt (This is how we teach the AI the format)
system_prompt = """
You are an expert agricultural AI data extractor. Analyze the Malayalam text and extract the relationships between entities.
Use relationship types like: AFFECTED_BY, TREATED_WITH, REQUIRES_INPUT, LOCATED_IN, CAUSES.

Here are examples of how you must format your output:

Example 1:
Text: "വാഴ കൃഷിയിൽ കാണപ്പെടുന്ന കുറുനാമ്പ് രോഗം തടയാൻ 5 മില്ലി വേപ്പെണ്ണ ഉപയോഗിക്കാം."
Output:
[
  {
    "subject": "വാഴ", "subject_type": "CROP",
    "relation": "AFFECTED_BY",
    "object": "കുറുനാമ്പ് രോഗം", "object_type": "DISEASE",
    "context": "കാണപ്പെടുന്ന"
  },
  {
    "subject": "വേപ്പെണ്ണ", "subject_type": "INPUT",
    "relation": "TREATED_WITH",
    "object": "കുറുനാമ്പ് രോഗം", "object_type": "DISEASE",
    "context": "5 മില്ലി, തടയാൻ"
  }
]

Example 2:
Text: "കേരളത്തിൽ തെങ്ങ് കൃഷിക്ക് ജൈവവളമായി ചാണകപ്പൊടി നൽകുക."
Output:
[
  {
    "subject": "തെങ്ങ്", "subject_type": "CROP",
    "relation": "LOCATED_IN",
    "object": "കേരളത്തിൽ", "object_type": "LOC",
    "context": ""
  },
  {
    "subject": "തെങ്ങ്", "subject_type": "CROP",
    "relation": "REQUIRES_INPUT",
    "object": "ചാണകപ്പൊടി", "object_type": "INPUT",
    "context": "ജൈവവളമായി"
  }
]

Now, process the following text and return ONLY the JSON array:
Text: 
"""

fully_annotated_dataset = []

print(f"Extracting relationships from {len(all_sentences)} sentences...")

# 4. The Processing Loop
for text in all_sentences:
    # We combine the training prompt with the specific sentence
    final_prompt = system_prompt + f'"{text}"'
    
    try:
        response = model.generate_content(final_prompt)
        
        # Clean the response to ensure it's valid JSON
        output_text = response.text.strip().replace('```json', '').replace('```', '')
        extracted_relations = json.loads(output_text)
        
        # Only save it if it actually found relationships
        if extracted_relations:
            fully_annotated_dataset.append({
                "text": text,
                "relationships": extracted_relations
            })
            print(f"Success: {text[:40]}...")
            
        time.sleep(13) # Respect the Google API Free Tier
        
    except Exception as e:
        print(f"Skipping sentence due to error/rate limit: {e}")
        time.sleep(13)

# 5. Save the final GraphRAG-ready JSON
with open("krishi_relations_ready.json", "w", encoding="utf-8") as f:
    json.dump(fully_annotated_dataset, f, ensure_ascii=False, indent=2)

print("Done! Dataset is now upgraded to a Property Graph format.")