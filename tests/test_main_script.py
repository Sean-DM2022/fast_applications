# --- Modules ---
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import json

# --- Define path ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Import functions from script ---
from main_script import extract_json_data
from main_script import create_prompt
from main_script import send_prompt
from main_script import create_tailored_resume

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
    test_resume_text = "resumetext4fun"
    return_prompt = create_prompt(test_job_description, test_resume_text, prompt_file="tests/test_prompt.txt")
    assert return_prompt == "Job: jobdescription4fun Resume: resumetext4fun"


def test_create_prompt_missing_fields():
    test_job_description = "jobdescription4fun"
    test_resume_text =  ""
    return_prompt = create_prompt(test_job_description, test_resume_text, prompt_file="tests/test_prompt.txt")
    assert return_prompt == "Job: jobdescription4fun Resume: "

# --- send_prompt ---
def test_send_prompt_mock_api():
    fake_ai_response = {
        "intro_paragraph": "I am a great fit for this role.",
        "keywords_list": ["Python", "Flask"],
        "missing_keywords": ["GitHub"],
        "skills": "Python | Flask | REST APIs"
    }
    # Utilizing MagicMock to intercept the API call for testing purposes
    mock_response = MagicMock()
    mock_response.text = json.dumps(fake_ai_response)

    # 'patch' intercepts the real Gemini call and returns our fake instead
    with patch("main_script.genai.Client") as mock_client:
        mock_client.return_value.models.generate_content.return_value = mock_response
        result = send_prompt("test prompt")

    assert result is not None
    new_intro, keywords_list, missing_keywords, skills = result
    assert new_intro == "I am a great fit for this role."
    assert "Python" in keywords_list
    assert "GitHub" in missing_keywords
    assert skills == "Python | Flask | REST APIs"

@pytest.mark.skip(reason="Real API call - run manually only")
def test_send_prompt_real_api():
    test_prompt = (
        "Respond ONLY with a valid JSON object containing exactly these keys: "
        "intro_paragraph (string), keywords_list (array of strings), "
        "missing_keywords (array of strings), skills (string). "
        "Use placeholder values."
    )
    result = send_prompt(test_prompt)
    assert result is not None
    new_intro, keywords_list, missing_keywords, skills = result
    assert isinstance(new_intro, str)
    assert isinstance(keywords_list, list)
    assert isinstance(skills, str)


# --- create_tailored_resume ---
def test_create_tailored_resume_mock():
    with (patch("main_script.drive_service") as mock_drive, patch("main_script.docs_service") as mock_docs):
        mock_drive.files().copy().execute.return_value = {"id": "fake_doc_id_123"}
        result = create_tailored_resume(
            record_id="R2D2",
            company="NOMA",
            job_title="Software Engineer",
            new_intro="I am a Software Engineer",
            skills="Python | Automation"
        )

        assert result == "https://docs.google.com/document/d/fake_doc_id_123"
        assert mock_drive.files().copy().execute.called
        assert mock_docs.documents().batchUpdate().execute.called

@pytest.mark.skip(reason="Real API call - run manually only")
def test_create_tailored_resume_real():
    result = create_tailored_resume(
        record_id="R2D2",
        company="NOMA",
        job_title="Software Engineer",
        new_intro="I am a Software Engineer",
        skills="Python | Automation"
    )
    assert result is not None
    assert result.startswith("https://docs.google.com/document/d/")