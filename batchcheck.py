import os
from google import genai

os.environ["GEMINI_API_KEY"] = "apikey"
client = genai.Client()

# Paste the Job ID the first script gave you!
JOB_ID = "batches/YOUR_BATCH_ID_HERE"

print(f"Checking status for {JOB_ID}...")
job = client.batches.get(name=JOB_ID)

print(f"Current State: {job.state}")

if job.state == "JOB_STATE_SUCCEEDED":
    print("Success! Your massive Property Graph is ready.")
    print(f"Check your Google Cloud / API Console for the output URI: {job.output_uri}")
elif job.state == "JOB_STATE_PENDING" or job.state == "JOB_STATE_RUNNING":
    print("Google's servers are still chewing through the data. Go grab a coffee!")
elif job.state == "JOB_STATE_FAILED":
    print("The job failed. Check your API console logs.")