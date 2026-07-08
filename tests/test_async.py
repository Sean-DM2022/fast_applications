# --- Modules ---
import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
import json
import requests
from fastapi.testclient import TestClient
import httpx2

# --- Define path ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Import functions from script ---
from core.config import base_retry, RetryableError, ClientError
from core.helpers import extract_json_data
from main_async import app, handle_response, request_content, request_fields, send_payload  # FastAPI client

def test_helpers_imported_from_async():
    result = extract_json_data({"entity": {"id": "abc123"}})
    assert result == "abc123"

def test_async_client():
    client = TestClient(app)
    response = client.post("/api/v1/doc/forge", json={})
    assert response.status_code == 401
    # 401 means the client exists and auth ran
    # 404 would mean client is offline





# --- request_content ---
test_page_id = "3123e484e34b8019bd4de26a14d50d72"

async def test_request_content_mock_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {"markdown": "# Software\n\nTitle section..."}
    with patch("httpx2.AsyncClient") as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        result = await request_content(test_page_id)
    assert result == "# Software\n\nTitle section..."

async def test_request_content_4xx():
        # This test NEEDS to touch the handle_response function
        # Constructing the response that will be read by handle_response
        # Needs to mock the raise_for_status behavior
    mock_error_response = MagicMock()
    mock_error_response.status_code = 404
    mock_error_response.text = "Not Found"
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx2.HTTPStatusError(
        message="Client error",
        request=MagicMock(),
        response=mock_error_response
    )   # From http2x documentation:  class HTTPStatusError(message, *, request, response)
    with patch("httpx2.AsyncClient") as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        with pytest.raises(ClientError):
            await request_content(test_page_id)
    assert mock_get.call_count == 1

async def test_request_content_5xx():
    mock_error_response = MagicMock()
    mock_error_response.status_code = 503
    mock_error_response.text = "Service Unavailable"
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx2.HTTPStatusError(
        message="Server error",
        request=MagicMock(),
        response=mock_error_response
    )
    with patch("httpx2.AsyncClient") as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        result = await request_content(test_page_id)
    assert result is None
    assert mock_get.call_count == 3 

@pytest.mark.skip(reason="Real API call - run manually only") # Has passed
async def test_request_content_real():
    result = await request_content(test_page_id)
    assert result is not None
    assert isinstance(result, str)



# --- request_fields ---
with open("tests/api-response.json", "r") as f:
    mock_fields_payload = json.load(f)

async def test_request_fields_mock_success():
    mock_response = MagicMock()
    mock_response.json.return_value = mock_fields_payload
    with patch("httpx2.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        result = await request_fields(test_page_id)
    assert result == (1, "Title", "Company")

async def test_request_fields_timeout():
    with patch("httpx2.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(side_effect=httpx2.TimeoutException("timeout"))
        result = await request_fields(test_page_id)
    assert result is None

async def test_request_fields_invalid_json():
    mock_response = MagicMock()
    mock_response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)
    with patch("httpx2.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        result = await request_fields(test_page_id)
    assert result is None

@pytest.mark.skip(reason="Real API call - run manually only") # Has passed
async def test_request_fields_real():
    result = await request_fields(test_page_id)
    assert result is not None
    record_id, doc_heading, company = result
    assert isinstance(record_id, int)
    assert isinstance(doc_heading, str)
    assert isinstance(company, str)


# --- send_payload ---
mock_payload = {
    "properties": {
        "status": {
            "status": { "name": "review_doc" },
        },
        "intro_paragraph": { "rich_text": [{ "text": { "content": "new_intro" } }] },
        "term_analysis": { "rich_text": [{ "text": { "content": "term_analysis" } }] },
        "gap_analysis": { "rich_text": [{ "text": { "content": "gap_analysis" } }] },
        "tailored_doc_url": { "url": "tailored_doc_url" },
        "highlights": { "rich_text": [{ "text": { "content": "highlights" } }] },
    },
}

async def test_send_payload_mock_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "object": "page",
        "id": "mock",
        "properties":{}
    }
    with patch("httpx2.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.patch = AsyncMock(return_value=mock_response)
        result = await send_payload(page_id="mock", payload=mock_payload)
    assert result == mock_response.json.return_value
    assert result["id"] == "mock"

@pytest.mark.skip(reason="Real API call - run manually only")
async def test_send_payload_real():
    result = request_fields(mock_fields_payload)
    assert result is not None



### handle_response: logic tests ###
async def test_handle_response_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {"key": "value"}
    result = await handle_response(mock_response)
    assert result == {"key": "value"}


async def test_handle_response_invalid_json():
    mock_response = MagicMock()
    mock_response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)
    result = await handle_response(mock_response)
    assert result is None


async def test_handle_response_5xx():
    error_response = MagicMock(status_code=503, text="Service Unavailable")
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx2.HTTPStatusError(
        message="error",
        request=MagicMock(),
        response=error_response
    )
    with pytest.raises(RetryableError):
        await handle_response(mock_response)


async def test_handle_response_4xx():
    error_response = MagicMock(status_code=404, text="Not Found")
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx2.HTTPStatusError(
        message="error",
        request=MagicMock(),
        response=error_response
    )
    with pytest.raises(ClientError):
        await handle_response(mock_response)