# Quiz App

Generate practice quizzes from pasted text, save them to SQLite, and export as JSON or Markdown.

## Deploy on Render

- Build command: `pip install -r requirements.txt && python quiz_project/manage.py collectstatic --noinput`
- Start command: `gunicorn quiz_project.wsgi:application --chdir quiz_project`
- Environment variables:
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL` (optional, defaults to `gpt-4o-mini`)
  - `DJANGO_SECRET_KEY`
  - `DJANGO_DEBUG` (set `0` in production)
  - `DJANGO_ALLOWED_HOSTS` (comma-separated)
  - `DJANGO_CSRF_TRUSTED_ORIGINS` (comma-separated, include https://your-app.onrender.com)
  - `DJANGO_SECURE_SSL_REDIRECT` (optional, defaults to `1`)
  - `MAX_INPUT_CHARS`, `MAX_UPLOAD_BYTES`
  - `RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW`

Note: The Django project lives inside the `quiz_project/` folder. The `--chdir quiz_project`
in the start command makes sure Python can import `quiz_project.wsgi`.
