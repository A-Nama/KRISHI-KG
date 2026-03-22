import pandas as pd
import re

# 1. Load your raw data
df = pd.read_csv("krishi_dataset.csv") 
raw_texts = df['Content'].dropna().tolist()

clean_sentences = []

for text in raw_texts:
    text = str(text)
    
    # FIX 1: Destroy literal escaped characters (the visible '\n' text)
    text = text.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', ' ')
    
    # FIX 2: Destroy actual hidden newline characters
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # FIX 3: Strip out Markdown formatting (like the ** in your snippet)
    text = text.replace('**', '').replace('*', '')
    
    # FIX 4: Flatten any giant gaps created by the replacements into a single space
    flat_text = re.sub(r'\s+', ' ', text)
    
    # Now split the perfectly flat text into sentences
    sentences = re.split(r'[.।!]+', flat_text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        # Keep sentences with more than 5 words
        if len(sentence.split()) > 5:
            clean_sentences.append(sentence)

# 3. Save the completely sanitized file
with open("krishi_ner_sanitized.txt", "w", encoding="utf-8") as f:
    for sent in clean_sentences:
        f.write(sent + "\n")

print(f"Sanitized and extracted {len(clean_sentences)} sentences!")