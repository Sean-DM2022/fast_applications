import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main_script import extract_json_data
from main_script import create_prompt

# --- extract_json_data ---
def test_extract_json_data_full():
    fake_payload = {
        "record_id": "abc123",
        "job_title": "Backend Developer",
        "company": "Acme Corp",
        "job_url": "https://acme.com/jobs/1",
        "job_description": "We need a Python dev"
    }
    record_id, job_title, company, job_url, job_description = extract_json_data(fake_payload)
    assert record_id == "abc123"
    assert job_title == "Backend Developer"
    assert company == "Acme Corp"

def test_extract_json_data_missing_fields():
    fake_payload = {
        "record_id": "xyz789"
    }
    record_id, job_title, company, job_url, job_description = extract_json_data(fake_payload)
    assert record_id == "xyz789"
    assert job_title == "Unknown Title"
    assert company == "Unknown Company"

# --- create_prompt ---
def test_create_prompt_full():
    test_job_description = "jobdescription4fun"
    test_resume_text =  "resumetext4fun"
    return_prompt = create_prompt(test_job_description, test_resume_text, prompt_file="tests/test_prompt.txt")
    assert return_prompt == "Job: jobdescription4fun Resume: resumetext4fun"


def test_create_prompt_missing_fields():
    test_job_description = "jobdescription4fun"
    test_resume_text =  ""
    return_prompt = create_prompt(test_job_description, test_resume_text, prompt_file="tests/test_prompt.txt")
    assert return_prompt == "Job: jobdescription4fun Resume: "