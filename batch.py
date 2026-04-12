import os
import json
from google import genai

# 1. Setup the new official SDK
os.environ["GEMINI_API_KEY"] = "api"
client = genai.Client()

system_prompt = """You are an expert agricultural AI data extractor. Analyze the Malayalam text and extract the relationships between entities.
Use relationship types like: AFFECTED_BY, TREATED_WITH, REQUIRES_INPUT, LOCATED_IN, CAUSES.

Format your output EXACTLY like this JSON array:
[
  {
    "subject": "വാഴ", "subject_type": "CROP",
    "relation": "AFFECTED_BY",
    "object": "കുറുനാമ്പ് രോഗം", "object_type": "DISEASE",
    "context": "കാണപ്പെടുന്ന"
  }
]
Text: """

# 2. Package sentences into JSONL
print("Packaging 409 sentences into JSONL format...")
with open("krishi_ner_clean.txt", "r", encoding="utf-8") as f:
    sentences = [line.strip() for line in f if line.strip()]

with open("batch_requests.jsonl", "w", encoding="utf-8") as f:
    for i, text in enumerate(sentences):
        full_prompt = system_prompt + f'"{text}"'
        
        # The strict schema required by the Gemini Batch API
        request_obj = {
            "key": f"req_{i}",
            "request": {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": full_prompt}]
                    }
                ]
            }
        }
        f.write(json.dumps(request_obj) + "\n")

# 3. Upload to Google's Servers
print("Uploading file to Google...")
uploaded_file = client.files.upload(
    file="batch_requests.jsonl", 
    config={"mime_type": "text/plain"}
)

# 4. Trigger the Asynchronous Batch Job
print("Triggering the cloud Batch Job...")
batch_job = client.batches.create(
    model="gemini-2.5-flash",
    src=uploaded_file.name
)

print("Job successfully submitted to the server farm!")
print("========================================")
print(f"YOUR JOB ID: {batch_job.name}")
print("========================================")
print("Save this Job ID! You will need it to download the results.")