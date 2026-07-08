# Changelog

Documented iteration changes

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
  