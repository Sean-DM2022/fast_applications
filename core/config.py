## Intro
'''
This script handles the following:
- Logging Configuration
- Loading Environment Variables
- Google OAuth 2.0 Workflow
'''


# --- Modules & Packages ---
import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
import logging
import requests
import httpx2
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# --- Logging Settings ---
logging.basicConfig(level=logging.WARNING) # DEBUG > INFO > WARNING > ERROR > CRITICAL
logger = logging.getLogger(__name__)

# --- Load Environment Variables ---
load_dotenv("/etc/secrets/.env") # Path for Render
load_dotenv("setup/.env") # Local Path

DATABASE_ACCESS_TOKEN = os.environ["NOTION_ACCESS_TOKEN"]
NOTION_VERIFICATION_TOKEN = os.environ["NOTION_VERIFICATION_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# --- Google OAuth 2.0 ---
SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/documents"]

def get_credentials():
    logging.debug("refresh_token: %s", bool(os.environ.get("GOOGLE_REFRESH_TOKEN")))
    logging.debug("client_id: %s", bool(os.environ.get("GOOGLE_CLIENT_ID")))
    logging.debug("client_secret: %s", bool(os.environ.get("GOOGLE_CLIENT_SECRET")))
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    creds.refresh(GoogleRequest())
    return creds

def get_drive_service(creds):
    drive_service = build("drive", "v3", credentials=creds)
    return drive_service

def get_docs_service(creds):
    docs_service = build("docs", "v1", credentials=creds)
    return docs_service


### Tenacity Setup Start
# --- Custom Exceptions ---
class RetryableError(Exception): # Timeouts, connection failures, 5xx — retry
    pass

class ClientError(Exception): # 4xx — don't retry
    pass


RETRYABLE = (
    RetryableError,
    httpx2.TimeoutException,
    httpx2.ConnectError,
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout
)

def log_retry(retry_state):
    exc = retry_state.outcome.exception()
    logger.warning(f"Attempt {retry_state.attempt_number} failed [{type(exc).__name__}]: Retrying...")

def retry_error(retry_state):
    exc = retry_state.outcome.exception()
    logger.error(f"Retry attempts exhausted [{type(exc).__name__}]: {exc}")
    return None

# --- Retry Decorator ---
def base_retry(func):
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type(RETRYABLE), # This will catch Timeout and ConnectionError exceptions
        before_sleep=log_retry,
        retry_error_callback=retry_error
    )(func)
### Tenacity Setup End