import pandas as pd
import re

def prep_krishi_data(input_csv="krishi_dataset.csv", output_txt="krishi_ner_clean.txt"):
    print("Starting Text-based Context Pipeline...")
    
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: Could not find {input_csv}.")
        return

    # FIX 0: The "Livestock Filter"
    if 'label' in df.columns:
        df_filtered = df[df['label'].astype(str).str.strip().str.upper() != 'LIVESTOCK']
    else:
        df_filtered = df

    # Find the ID column
    id_col = next((col for col in df_filtered.columns if col.lower() == 'id'), None)
    
    # FIX 1: Group by ID (if it exists) so split rows become one context block
    if id_col:
        # This merges all text that shares the same ID into a single string
        df_grouped = df_filtered.groupby(id_col)['Content'].apply(lambda x: ' '.join(x.dropna().astype(str))).reset_index()
    else:
        df_grouped = df_filtered

    clean_paragraphs = []

    for index, row in df_grouped.iterrows():
        raw_text = str(row.get('text', row.get('Content', '')))
        
        # 1. Eradicate hidden newlines so the paragraph stays strictly on ONE line
        clean_text = raw_text.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', ' ')
        clean_text = clean_text.replace('\n', ' ').replace('\r', ' ')

        # 2. Strict Character Filtering (Malayalam, English, Numbers, Punctuation ONLY)
        strict_regex = r'[^\u0D00-\u0D7Fa-zA-Z0-9\s.,;!?()\'"%\-]'
        clean_text = re.sub(strict_regex, ' ', clean_text)
        
        # 3. Flatten multiple spaces
        flat_text = re.sub(r'\s+', ' ', clean_text).strip()

        # 4. Quality Control
        if len(flat_text.split()) > 4:
            # We only append the text, leaving the ID behind in the void
            clean_paragraphs.append(flat_text)

    # Output to a simple TXT file
    with open(output_txt, "w", encoding="utf-8") as f:
        for para in clean_paragraphs:
            f.write(para + "\n")

    print(f"Success! Saved {len(clean_paragraphs)} clean, grouped paragraphs to {output_txt}.")

if __name__ == "__main__":
    prep_krishi_data()