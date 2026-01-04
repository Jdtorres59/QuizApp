import json
import os

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from .models import Quiz
from .services import format_quiz_markdown, generate_quiz


ALLOWED_UPLOAD_EXTENSIONS = {".txt", ".md"}


def _parse_quiz_json(raw_json):
    if not raw_json:
        return None
    try:
        return json.loads(raw_json)
    except json.JSONDecodeError:
        return None


def _decorate_questions(quiz_data):
    if not isinstance(quiz_data, dict):
        return quiz_data
    questions = quiz_data.get("questions")
    if not isinstance(questions, list):
        return quiz_data
    letters = ["A", "B", "C", "D"]
    for question in questions:
        answer_index = question.get("answer_index")
        answer_letter = ""
        if isinstance(answer_index, int):
            if 0 <= answer_index < len(letters):
                answer_letter = letters[answer_index]
            elif 1 <= answer_index <= len(letters):
                answer_letter = letters[answer_index - 1]
        question["answer_letter"] = answer_letter
    return quiz_data


def _quiz_filename(quiz, extension):
    base = slugify(quiz.title) or f"quiz-{quiz.pk}"
    return f"{base}.{extension}"


def _get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _rate_limit_exceeded(request):
    rate_limit = getattr(settings, "RATE_LIMIT_REQUESTS", 5)
    window = getattr(settings, "RATE_LIMIT_WINDOW", 60)
    if rate_limit <= 0 or window <= 0:
        return False
    ip = _get_client_ip(request)
    if not ip:
        return False
    cache_key = f"quiz_rate:{ip}"
    count = cache.get(cache_key, 0)
    if count >= rate_limit:
        return True
    cache.set(cache_key, count + 1, timeout=window)
    return False


def home(request):
    context = {
        "form_values": {
            "title": "",
            "text": "",
            "num_questions": "10",
            "difficulty": "medium",
            "language": "EN",
        }
    }
    if request.method == "POST":
        title = request.POST.get("title", "").strip()[:200]
        text = request.POST.get("text", "").strip()
        num_questions = request.POST.get("num_questions", "10")
        difficulty = request.POST.get("difficulty", "medium")
        language = request.POST.get("language", "EN")
        upload = request.FILES.get("upload")

        context["form_values"] = {
            "title": title,
            "text": text,
            "num_questions": num_questions,
            "difficulty": difficulty,
            "language": language,
        }

        if upload and not text:
            ext = os.path.splitext(upload.name)[1].lower()
            if ext not in ALLOWED_UPLOAD_EXTENSIONS:
                context["error"] = "Only .txt or .md files are supported."
                return render(request, "base.html", context)
            if upload.size > settings.MAX_UPLOAD_BYTES:
                context["error"] = "Uploaded file is too large."
                return render(request, "base.html", context)
            text = upload.read().decode("utf-8", errors="ignore").strip()
            context["form_values"]["text"] = text

        if not text:
            context["error"] = "Please add some text to generate a quiz."
            return render(request, "base.html", context)
        if len(text) > settings.MAX_INPUT_CHARS:
            context["error"] = "Text is too long. Please shorten it and try again."
            return render(request, "base.html", context)

        allowed_difficulties = {"easy", "medium", "hard"}
        allowed_languages = {"EN", "ES"}
        if difficulty not in allowed_difficulties:
            difficulty = "medium"
        if language not in allowed_languages:
            language = "EN"

        if _rate_limit_exceeded(request):
            context["error"] = "Too many requests. Please wait a minute and try again."
            return render(request, "base.html", context, status=429)

        try:
            num_questions_int = int(num_questions)
        except ValueError:
            num_questions_int = 10
        if num_questions_int not in (5, 10, 15):
            num_questions_int = 10

        try:
            result = generate_quiz(
                text=text,
                num_questions=num_questions_int,
                difficulty=difficulty,
                language=language,
                title=title,
            )
        except Exception as exc:
            context["error"] = f"Quiz generation failed: {exc}"
            return render(request, "base.html", context)

        quiz = Quiz(
            title=title,
            input_text=text,
            output_text=result["raw_output"],
            question_count=result["question_count"],
        )
        quiz_data = result["json"] if isinstance(result["json"], dict) else None
        if quiz_data:
            quiz.output_json = json.dumps(quiz_data, ensure_ascii=False, indent=2)
            quiz.title = (title or quiz_data.get("title") or "Untitled Quiz")[:200]
        else:
            quiz.title = (title or "Untitled Quiz")[:200]
        quiz.save()
        return redirect(f"{reverse('quiz_detail', args=[quiz.pk])}?saved=1")

    return render(request, "base.html", context)


def history(request):
    quizzes = Quiz.objects.order_by("-created_at")
    return render(request, "history.html", {"quizzes": quizzes})


def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    quiz_data = _parse_quiz_json(quiz.output_json)
    quiz_data = _decorate_questions(quiz_data)
    markdown = format_quiz_markdown(quiz_data, fallback_title=quiz.title) if quiz_data else ""
    context = {
        "quiz": quiz,
        "quiz_data": quiz_data,
        "markdown": markdown,
        "saved": request.GET.get("saved") == "1",
    }
    return render(request, "quiz_detail.html", context)


def download_json(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    content = quiz.output_json or quiz.output_text or ""
    response = HttpResponse(content, content_type="application/json")
    response["Content-Disposition"] = f'attachment; filename="{_quiz_filename(quiz, "json")}"'
    return response


def download_markdown(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    quiz_data = _parse_quiz_json(quiz.output_json)
    markdown = format_quiz_markdown(quiz_data, fallback_title=quiz.title) if quiz_data else ""
    content = markdown or quiz.output_text or ""
    response = HttpResponse(content, content_type="text/markdown")
    response["Content-Disposition"] = (
        f'attachment; filename="{_quiz_filename(quiz, "md")}"'
    )
    return response


@require_POST
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    quiz.delete()
    return redirect("history")
