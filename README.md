# Quiz App

## Overview
Quiz App turns pasted text (or uploaded `.txt/.md` files) into structured practice quizzes using the OpenAI API. Users pick question count, difficulty, and output language. Generated quizzes are saved to SQLite, shown in a History view, and can be exported as JSON or Markdown.

## Why I Built It
I wanted a clean, portfolio‑ready Django project that demonstrates practical AI usage, thoughtful UX, and a real workflow: generate → review → export → revisit.

## Demo
- Live Demo: [Live Demo URL]
- Repo: [Repo URL]

## Key Features
- Create quizzes from text or file upload
- Controls for question count, difficulty, and language
- Structured JSON output with fallback display
- History list (newest first) with view, download, delete
- Export formats: JSON + Markdown

## Tech Stack
Python, Django (templates), SQLite, OpenAI API, Gunicorn, Render (free tier)

## How It Works (High‑Level)
1. User submits text + options.
2. Backend prompts OpenAI for JSON‑only quiz output.
3. Quiz is stored in SQLite and rendered in the UI.
4. History lists saved quizzes and provides downloads.

## Local Setup (2 minutes)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here
python quiz_project/manage.py migrate
python quiz_project/manage.py runserver
```

## Deploy on Render
- Build command:
  ```
  pip install -r requirements.txt && python quiz_project/manage.py collectstatic --noinput && python quiz_project/manage.py migrate
  ```
- Start command:
  ```
  gunicorn quiz_project.wsgi:application --chdir quiz_project
  ```
- Required env vars:
  - `OPENAI_API_KEY`
  - `DJANGO_SECRET_KEY`
  - `DJANGO_DEBUG=0`
  - `DJANGO_ALLOWED_HOSTS`
  - `DJANGO_CSRF_TRUSTED_ORIGINS`

## Notes on Persistence & Limits
Render free tier uses ephemeral storage. SQLite persistence is best‑effort and may reset after redeploys. Input size limits and basic rate limiting help control API usage.

## Status
Active / portfolio‑ready.

## .env Example
```env
OPENAI_API_KEY=your_key_here
DJANGO_SECRET_KEY=your_secret_here
DJANGO_DEBUG=1
```

Security note: never commit API keys or secrets to the repo.
