import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main_script import extract_json_data

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