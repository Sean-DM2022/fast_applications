# fast_applications

# Intro

This script was originally designed for automating the process of tailoring resumes for job applications. It does so using the following app tools:
- Database: Notion (for its free API and ease of use for project management applications)
- Browser Extension: "Save to Notion" (This is how I added tasks to the workflow)
- Cloud Drive: Google Drive (Free api and ability to create documents)
- Host Server: Render (Free api and free tier for simple applications. Can be hosted locally)
- GenAI: Google Gemini: (Free API and use tier for their flash model. ChatGPT at the time of this script being created no longer had a free use tier)

You will need to do a little setup for it to work on your own. This involve:
- Finding your API keys
- 

## Scalability

I plan to make this script as scalable and customizable as possible. This means that you will be able to adjust for:
- Names of database fields
- Total number of fields
- The prompt sent to the AI
- The number of fields you wish to update on your form

What will not be easily scalable at this point:
- GenAI selection: limited to Google Gemini
- Document Storage: Google Drive
- Type of document used: Google Doc (NOT MS Word - aka .docx)


## Instructions

Below I explain the use for each file in the root folder and how to make adjustments to the script without needing to touch the code. Please feel free to message me on GitHub should you have any questions.

Create a ".env" file in the root folder. Use the following as a draft:
---
# Local Storage of keys and passwords
notion_local_api_key=
gemini_local_api_key=
my_local_client_password=
---

## prompt.txt

Here, you will type up the prompt you will want to send to the AI. No comments here. The whole file will be read and sent.

TAGS

tags should be surrounded by two curly brackets: {{tag_example}}


## config.json

Here you will add information that is not importing from Notion.


## Initial Setup

You will need the API keys for your notion and for the copy of Gemini you wish to use.
You will also need to know the password you will be using for your client server.

Create a ".env" file in the root folder and store your keys and passwords there.



## Where to place your resume

I debated on where the best place to store your resume would be. Should it use a text file like it does for the prompt? I ultimately decided to go with having the script pull the resume text from a Google Doc, allowing for a more dynamic workflow. Your resume is more likely to change over time than the prompt.

I use a base or general resume when submitting the prompt to the AI. When tailoring the resume with the AI suggestions, I use a copy of the base resume with the corresponding sections replaced with {{TAGS}} as my template. This makes for a more fluid experinece.




## Hosting Locally vs a Server

As I moved between computers often, I opted to host my script using <https://render.com/>. They have a free tier you can use for personal apps. Keep in mind that the server goes dormant with inactivity exceeding 15 mins. This just means there will be a delay while the server wakes up (30-60 seconds).

Flask allows you to host the server locally.