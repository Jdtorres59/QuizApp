import json

from openai import OpenAI

from . import config


def _get_client():
    if config.API_KEY:
        return OpenAI(api_key=config.API_KEY)
    return OpenAI()


def _safe_json_loads(raw_text):
    if not raw_text:
        return None
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw_text[start : end + 1])
            except json.JSONDecodeError:
                return None
    return None


def generate_quiz(text, num_questions=10, difficulty="medium", language="EN", title=""):
    if not config.API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")
    client = _get_client()
    system_prompt = (
        "You are a quiz generator. Return valid JSON only with this schema: "
        '{"title":"...", "questions":[{"question":"...", "choices":["A","B","C","D"], '
        '"answer_index":0, "explanation":"optional short"}]}. '
        "Use answer_index as a zero-based integer. Do not include Markdown or code fences."
    )
    user_prompt = (
        f"Create {num_questions} multiple choice questions.\n"
        f"Difficulty: {difficulty}.\n"
        f"Language: {language}.\n"
        f"Title (if provided): {title or 'Generate a short title'}.\n"
        f"Source text:\n{text}"
    )
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1800,
        temperature=0.7,
    )
    raw_output = (response.choices[0].message.content or "").strip()
    data = _safe_json_loads(raw_output)
    question_count = len(data.get("questions", [])) if isinstance(data, dict) else 0
    return {
        "raw_output": raw_output,
        "json": data,
        "question_count": question_count,
    }


def format_quiz_markdown(quiz_data, fallback_title="Quiz"):
    if not isinstance(quiz_data, dict):
        return ""
    title = quiz_data.get("title") or fallback_title
    questions = quiz_data.get("questions") or []
    lines = [f"# {title}", ""]
    for index, question in enumerate(questions, start=1):
        q_text = question.get("question") or ""
        lines.append(f"## {index}. {q_text}")
        choices = question.get("choices") or []
        for idx, choice in enumerate(choices):
            letter = chr(ord("A") + idx)
            lines.append(f"- {letter}. {choice}")
        answer_index = question.get("answer_index")
        answer_letter = ""
        if isinstance(answer_index, int):
            if 0 <= answer_index < len(choices):
                answer_letter = chr(ord("A") + answer_index)
            elif 1 <= answer_index <= len(choices):
                answer_letter = chr(ord("A") + answer_index - 1)
        if answer_letter:
            lines.append(f"**Answer:** {answer_letter}")
        explanation = question.get("explanation") or ""
        if explanation:
            lines.append(f"**Explanation:** {explanation}")
        lines.append("")
    return "\n".join(lines).strip()
