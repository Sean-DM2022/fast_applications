## Intro


# --- Modules & Packages ---
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from google import genai
from google.genai import types
from googleapiclient.discovery import build
from google.oauth2 import service_account

# --- Keys ---
load_dotenv()
database_api_key = os.getenv("notion_local_api_key")
gemini_api_key = os.getenv("gemini_local_api_key")
my_client_password = os.getenv("my_local_client_password")

# --- Configuration File ---
with open("config.json", "r") as f:
    config = json.load(f)

my_name = config["my_name"]

# --- Google Service Account ---
SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/documents"]
creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
drive_service = build("drive", "v3", credentials=creds)
docs_service = build("docs", "v1", credentials=creds)


# --- Initial Setup ---
app = Flask(__name__)
now = datetime.now()
current_month = now.month
current_year = now.year

# --- Helper Functions ---

def extract_json_data(incoming_data): # Process the API call from Notion
    print("Call received! Data payload: ", incoming_data)
    print("Extracting data...")
    try:
        record_id = incoming_data.get("record_id")
        job_title = incoming_data.get("job_title", "Unknown Title")
        company = incoming_data.get("company", "Unknown Company")
        job_url = incoming_data.get("job_url", "No URL provided")
        job_description = incoming_data.get("job_description", "No Description provided")
        print("Successfully parsed JSON")
        return record_id, job_title, company, job_url, job_description

    except json.JSONDecodeError:
        print("Failed to parse JSON")
        return None

def scrape_resume(google_doc_url): # Pull Resume TEXT from Google Drive
    return resume_text
    pass

def create_prompt(job_description, resume_text, prompt_file="prompt.txt"): # Call prompt.txt, insert current resume TEXT and job description TEXT
    with open(prompt_file, "r") as f:
        prompt = f.read()
    prompt = prompt.replace("{{notion_job_description}}", job_description)
    prompt = prompt.replace("{{base_resume_text}}", resume_text)
    return prompt
# Add a try/exception to make sure the job_description and resume_text are not blank.

def send_prompt(prompt): # Send & Receive
    client = genai.Client(api_key=gemini_api_key)
    print("Sending prompt to Gemini. Please wait...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        print("Response from AI received!")
        print("Parsing response...")
        try:
            ai_data = json.loads(response.text)

            new_intro = ai_data.get("intro_paragraph", "")
            keywords_list = ai_data.get("keywords_list", [])
            missing_keywords = ai_data.get("missing_keywords", [])
            skills = ai_data.get("skills", "")
            print("Successfully parsed AI response!")
            return new_intro, keywords_list, missing_keywords, skills

        except json.JSONDecodeError as json_err:
            print(f"Failed to parse AI response: {json_err}")
            print("Adjust your prompt to not include conversational text.")
            return None
    
    except Exception as err:
        print(f"AI call failed: {err}")
        return None
# Add to the send_prompt function a retry loop in case of receiving a 503 error from Gemini
# Add an API call if retries are exhausted to update the status to "need_to_rerun".

def create_tailored_resume(record_id, company, job_title, new_intro, skills): # Create new google doc from template and save URL
    # Copy the template Doc
    template_id = config["resume_template_id"]
    response = drive_service.files().copy( # command to copy a google doc
        fileId=template_id, # selects the proper file
        body={"name": f"{record_id} - Resume - {company} ({current_month} {current_year})"} # Name of the new file
    ).execute()
    new_doc_id = response["id"]

    # Replace {{tags}}
    docs_service.documents().batchUpdate(
        documentId=new_doc_id,
        body={"requests": [
            {"replaceAllText": {"containsText": {"text": "{{job_title}}"}, "replaceText": job_title}},
            {"replaceAllText": {"containsText": {"text": "{{introduction_paragraph}}"}, "replaceText": new_intro}},
            {"replaceAllText": {"containsText": {"text": "{{skills}}"}, "replaceText": skills}},
        ]}
    ).execute()

    # Return URL
    tailored_resume_url = f"https://docs.google.com/document/d/{new_doc_id}"
    print(f"Tailored resume created: {tailored_resume_url}")
    return tailored_resume_url
    pass

def create_payload(): # Prepare JSON payload for Notion
    pass

def send_payload(outgoing_data): # Push API call to Notion
    pass


# --- Main Webhook ---
@app.route('/api/v1/resume-build', methods=['POST'])
def handle_webhook():
    provided_key = request.headers.get('Authorization')
    if provided_key != f"Bearer {my_client_password}":
        return jsonify({"status": "error", "message": "Unauthorized request"}), 401

    incoming_data = request.json
    if not incoming_data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    result = extract_json_data(incoming_data)
    if result is None:
        return jsonify({"status": "error", "message": "Failed to parse data"}), 400
    record_id, job_title, company, job_url, job_description = result

    result = scrape_resume()
    if result is None:
        return jsonify({"status": "error", "message": "Failed to pull resume"}), 400
    resume_text = result

    result = create_prompt(job_description, resume_text, prompt_file="prompt.txt")
    if result is None:
        return jsonify({"status": "error", "message": "Failed to create prompt"}), 400
    prompt = result

    result = send_prompt(prompt)
    if result is None:
        return jsonify({"status": "error", "message": "AI call failed"}), 400
    new_intro, keywords_list, missing_keywords, skills = result
    
    create_tailored_resume()

    outgoing_data = create_payload()
    send_payload(outgoing_data)

    return jsonify({"status": "success", "message": "Processing data"}), 200

if __name__ == '__main__':
    print("Starting local server on port 5000...")
    app.run(port=5000)