## Intro


# --- Modules & Packages ---
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from google import genai
from google.genai import types

# --- Keys ---
load_dotenv()
notion_api_key = os.getenv("notion_local_api_key")
gemini_api_key = os.getenv("gemini_local_api_key")
my_client_password = os.getenv("my_local_client_password")

# --- Initial Setup ---
app = Flask(__name__)
my_name = "Sean Modawell"
now = datetime.now()
current_month = now.month
current_year = now.year

# --- Helper Functions ---

def extract_json_data(incoming_data): # Process the API call from Notion
    print("Call received! Data payload: ", incoming_data)
    print("Extracting data...")
    try:
        notion_record_id = incoming_data.get("record_id")
        notion_job_title = incoming_data.get("job_title", "Unknown Title")
        notion_company = incoming_data.get("company", "Unknown Company")
        notion_job_url = incoming_data.get("job_url", "No URL provided")
        notion_job_description = incoming_data.get("job_description", "No Description provided")
        print("Successfully parsed JSON")
        return notion_record_id, notion_job_title, notion_company, notion_job_url, notion_job_description

    except json.JSONDecodeError:
        print("Failed to parse JSON")
    pass

def scrape_resume(google_doc_url): # Pull Resume TEXT from Google Drive
    return resume_text
    pass

def create_prompt(job_description, resume_text, prompt_file="prompt.txt"): # Call prompt.txt, insert current resume TEXT and job description TEXT
    with open(prompt_file, "r") as f:
        prompt = f.read()
    prompt = prompt.replace("{{job_description}}", job_description)
    prompt = prompt.replace("{{resume_text}}", resume_text)
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
    
    except Exception as err:
        print(f"AI call failed: {err}")
    pass

def create_tailored_resume(): # Create new google doc from template and save URL
    pass

def create_payload(): # Prepare JSON payload for Notion
    pass

def send_payload(outgoing_data): # Push API call to Notion
    pass


# --- Main Webhook ---
@app.route('/api/v1/resume-build', methods=['POST'])
def handle_wekbhook():
    provided_key = request.headers.get('Authorization')
    if provided_key != f"Bearer {my_client_password}":
        return jsonify({"status": "error", "message": "Unauthorized request"}), 401

    incoming_data = request.json
    if not incoming_data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    extract_json_data(incoming_data)
    scrape_resume()
    create_prompt()
    send_prompt()
    create_tailored_resume()
    outgoing_data = create_payload()
    send_payload(outgoing_data)

    return jsonify({"status": "success", "message": "Processing data"}), 200

if __name__ == '__main__':
    print("Starting local server on port 5000...")
    app.run(port=5000)