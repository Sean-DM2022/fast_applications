# fast_applications

An automation pipeline for tailoring resumes to job postings using Notion, Google Gemini, and Google Drive.

-----

## Overview

Job applications are time-consuming. This script automates the most tedious part: reading a job posting and getting AI-powered suggestions for how to tailor your resume to it.

The workflow:

1. You save a job posting to Notion using the **Save to Notion** browser extension
1. Notion sends a webhook to this app
1. The app pulls the job data, fetches your base resume from Google Drive, and sends everything to **Google Gemini**
1. Gemini returns structured tailoring suggestions
1. The results are saved to a new **Google Doc** for your review before applying

The app is built with **Flask** and can be hosted locally or on a free [Render](https://render.com/) instance.

-----

## Tools Used

|Purpose             |Tool                      |Why                                     |
|--------------------|--------------------------|----------------------------------------|
|Task/job database   |Notion                    |Free API, great for project management  |
|Browser clipping    |Save to Notion (extension)|Easy way to add jobs to the workflow    |
|Resume + doc storage|Google Drive / Google Docs|Free API, dynamic and easy to update    |
|AI suggestions      |Google Gemini (Flash)     |Free API tier; ChatGPT no longer has one|
|Server hosting      |Render                    |Free tier for personal apps             |
|Web framework       |Flask                     |Lightweight; supports local hosting too |

-----

## File Reference

### `.env`

Stores your secret keys. **Never commit this file to version control.**

Create a `.env` file in the root folder using this template:


# Local storage of keys and passwords
notion_local_api_key=
gemini_local_api_key=
my_local_client_password=


### `prompt.txt`

The prompt sent to Gemini. The entire contents of this file are read and submitted as-is — no comments are supported.

Use `{{double_curly_braces}}` for dynamic tags that get replaced at runtime. For example:


Here is a job description: {{job_description}}
Here is my resume: {{resume_text}}


### `config.json`

Configuration that doesn’t belong in `.env`. This is where you adjust things like Notion database field names or the number of fields you want to process — without touching the Python code.

-----

## Setup Instructions

### 1. Get your API keys

- **Notion**: Go to [notion.so/my-integrations](https://www.notion.so/my-integrations), create a new integration, and copy the secret key. Make sure your integration has access to the database you’re using.
- **Gemini**: Go to [aistudio.google.com](https://aistudio.google.com) and generate an API key.
- **Google Drive / Docs**: Set up a service account in the [Google Cloud Console](https://console.cloud.google.com/), enable the Drive and Docs APIs, and download the credentials JSON.
- **Client password**: Choose any password. This is used to authenticate requests to your Flask server.

### 2. Configure your `.env`

Copy the template above into a new `.env` file in the root folder and fill in your keys.

### 3. Set up your resume in Google Drive

Store your **base resume** as a Google Doc. The script fetches it fresh on each run, so any updates you make to the doc are automatically picked up.

For applying, it’s recommended to maintain a second Google Doc as a **template**, a copy of your base resume with sections replaced by `{{TAGS}}`. Gemini’s suggestions can then be slotted directly into the template.

### 4. Write your prompt

Edit `prompt.txt` with the instructions you want to send to Gemini. Use `{{tags}}` to reference dynamic values like the job description or your resume text. The quality of AI output depends heavily on prompt quality — see the note below.

### 5. Configure `config.json`

Adjust field names and settings to match your Notion database setup.

-----

## Hosting

### Locally (Flask)

Flask’s built-in server lets you run the app on your machine. Useful for testing or if you’re always on the same computer.


### On Render (recommended for portability)

[Render](https://render.com/) offers a free tier that works well for personal automation apps. Connect your GitHub repo and it will deploy automatically on each push.

> **Note:** Free Render instances go dormant after 15 minutes of inactivity. Expect a 30–60 second delay on the first webhook while the instance wakes up.

-----

## A Note on Prompt Design

The quality of Gemini’s suggestions depends entirely on the quality of your prompt. Vague or incomplete prompts lead to unhelpful output, which defeats the purpose of this automation.

A good prompt typically includes:

- Clear instructions on what you want (e.g., “suggest edits to the bullet points under Experience”)
- The full job description
- Your base resume
- The format you want the response in (the app expects structured JSON)

Treat your `prompt.txt` as something worth iterating on. Small improvements to the prompt can have a big impact on the output.

-----

## What’s Configurable (Without Touching Code)

**You can adjust:**

- Notion database field names
- Total number of fields processed
- The prompt sent to Gemini
- The number of output fields

**Currently not configurable:**

- AI provider (locked to Google Gemini)
- Document storage (locked to Google Drive)
- Document format (Google Docs only — not `.docx`)

-----

## Questions?

Feel free to open an issue or reach out via GitHub. Contributions and suggestions are welcome.