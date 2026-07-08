# Changelog

Documented iteration changes

---

## [v1.1.1] Async Release - 2026-07-07

Support added for Rate Limits: 429 HTTP error codes

- 429 (Too Many Requests)
- Each API has unique rate limits based on different parameters
- Rate limits are used for billing and server regulation

Gemini API
      - Requests per minute (RPM)
      - Tokens per minute (TPM) - Usually associated with AI/LLM Models
      - Requests per day (RPD)

- Gemini 3.1 Flash Lite
      - RPM = 15
      - TPM = 250K
      - RPD = 500

- Gemini 3.5 Flash
      - RPM = 5
      - TPM = 250K
      - RPD = 20

Notion API
      - Rate
          - 3 requests per second
      - Size Limit per Property
          - Rich text = 2000 characters
          - URL/Email/Phone = 200 characters
      - Payload
          - 1000 Block Elements
          - 500 KB

[Gemini API Rate Limit](https://aistudio.google.com/rate-limit?)
[Notion Request Limits](https://developers.notion.com/reference/request-limits)

---

## [v1.1] Async Release - 2026-07-07

This release features several significant updates:

1. Revamped repo architecture to lessen clutter
    - Files and folders renamed
    - Helper functions
2. The main script now has a **sync** and **async** version
   - Flask and Requests library replaced by FastAPI and HTTPX in the **async** version
3. Added `INSTALL.md` for detailed instructions
4. Expanded exception handling and pytest-suite
    - Implemented [tenacity](https://github.com/jd/tenacity) library
    - Retry decorator with exponential backoff - see [config.py](core/config.py)
    - Soft failure handling for **Recoverable errors**:
        - Timeouts
        - Connection errors
        - 5xx HTTP errors
    - Fail-fast behaviour for **Non-recoverable errors**:
        - 4xx HTTP errors
        - Includes 429 errors (Too Many Requests) at this time

---

## [v1.0] Initial Release - 2026-05-13

- Fully functioning for personal use
  