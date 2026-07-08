# --- Modules ---
import pytest
import sys
import os

from core.config import base_retry, RetryableError, ClientError

# --- Define path ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

## Tests

## base_retry: logic tests ###
async def test_base_retry_success():
    calls = []

    @base_retry
    async def attempt():
        calls.append(1)
        return "ok"

    result = await attempt()
    assert result == "ok"
    assert len(calls) == 1

async def test_base_retry_retryable_error():
    calls = []

    @base_retry
    async def attempt():
        calls.append(1)
        raise RetryableError("error")

    result = await attempt()
    assert result is None
    assert len(calls) == 3

async def test_base_retry_client_error():
    calls = []

    @base_retry
    async def bad_request():
        calls.append(1)
        raise ClientError("400")

    with pytest.raises(ClientError):
        await bad_request()
    assert len(calls) == 1
