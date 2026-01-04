# Quiz App

Generate practice quizzes from pasted text, save them to SQLite, and export as JSON or Markdown.

## Deploy on Render

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn quiz_project.wsgi:application`
- Environment variables:
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL` (optional, defaults to `gpt-4o-mini`)
